import secrets
from django.db import models
from django.utils import timezone


class MatterFabric(models.Model):
    """
    Repräsentiert die Matter-Fabric für einen Haushalt.
    """
    home = models.OneToOneField(
        "devices.Home",
        on_delete=models.CASCADE,
        related_name="matter_fabric",
    )
    fabric_id = models.BigIntegerField(
        help_text="64-Bit Matter Fabric ID",
        unique=True,
    )
    controller_node_id = models.BigIntegerField(
        default=1,
        help_text="Node-ID des Sharegy Matter Controllers",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "matter"
        verbose_name = "Matter Fabric"
        verbose_name_plural = "Matter Fabrics"

    def __str__(self):
        return f"Fabric {hex(self.fabric_id)} (Home: {self.home_id})"

    @classmethod
    def get_or_create_for_home(cls, home):
        fabric = cls.objects.filter(home=home).first()
        if not fabric:
            # Generiere eine eindeutige 64-Bit Fabric ID
            fabric_id = int(secrets.token_hex(7), 16)
            fabric = cls.objects.create(
                home=home,
                fabric_id=fabric_id,
                controller_node_id=1,
            )
        return fabric


class MatterNode(models.Model):
    """
    Repräsentiert ein gekoppeltes Matter-Endgerät (Matter 1.3).
    """
    DEVICE_TYPE_CHOICES = [
        ("smart_plug", "Smart Plug / Zwischenstecker (On/Off + Energy)"),
        ("evse", "Matter EVSE / Wallbox"),
        ("solar_inverter", "Solar-Wechselrichter / BKW"),
        ("battery", "Batteriespeicher"),
        ("heatpump", "Wärmepumpe"),
        ("meter", "Stromzähler / Sub-Meter"),
    ]

    fabric = models.ForeignKey(
        MatterFabric,
        on_delete=models.CASCADE,
        related_name="nodes",
    )
    node_id = models.BigIntegerField(
        help_text="Eindeutige Matter Node ID innerhalb der Fabric"
    )
    device = models.OneToOneField(
        "devices.Device",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="matter_node",
    )
    name = models.CharField(max_length=128)
    device_type = models.CharField(
        max_length=64,
        choices=DEVICE_TYPE_CHOICES,
        default="smart_plug",
    )
    device_type_id = models.IntegerField(
        default=0x010A, # On/Off Plug-in Unit
        help_text="Standard Matter Device Type ID (Hex)",
    )
    vendor_id = models.IntegerField(default=0xFFF1)
    product_id = models.IntegerField(default=0x8001)
    discriminator = models.IntegerField(default=3840)
    setup_pin = models.CharField(max_length=32, blank=True)
    manual_code = models.CharField(max_length=32, blank=True)
    qr_payload = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    is_online = models.BooleanField(default=True)
    firmware_version = models.CharField(max_length=64, default="1.3.0")
    attributes_payload = models.JSONField(default=dict, blank=True)
    last_seen_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "matter"
        unique_together = ("fabric", "node_id")
        verbose_name = "Matter Node"
        verbose_name_plural = "Matter Nodes"
        ordering = ["node_id"]

    def __str__(self):
        return f"Node {self.node_id}: {self.name} ({self.device_type})"


class MatterEndpoint(models.Model):
    """
    Repräsentiert einen Endpunkt (Endpoint) auf einem Matter-Node.
    """
    node = models.ForeignKey(
        MatterNode,
        on_delete=models.CASCADE,
        related_name="endpoints",
    )
    endpoint_id = models.IntegerField(default=1)
    name = models.CharField(max_length=64, default="Endpoint 1")
    device_type_id = models.IntegerField(default=0x010A)

    class Meta:
        app_label = "matter"
        unique_together = ("node", "endpoint_id")
        verbose_name = "Matter Endpoint"
        verbose_name_plural = "Matter Endpoints"

    def __str__(self):
        return f"Node {self.node.node_id} / Endpoint {self.endpoint_id}"


class MatterCluster(models.Model):
    """
    Repräsentiert einen Matter Cluster auf einem Endpunkt.
    Unterstützt Matter 1.3 Energy Management Cluster:
    - 0x0090: Electrical Power Measurement
    - 0x0091: Electrical Energy Measurement
    - 0x0006: On/Off
    - 0x0098: Device Energy Management
    - 0x0099: EVSE
    """
    CLUSTER_DEFINITIONS = {
        0x0006: "On/Off Cluster",
        0x0008: "Level Control Cluster",
        0x0090: "Electrical Power Measurement (Matter 1.3)",
        0x0091: "Electrical Energy Measurement (Matter 1.3)",
        0x0098: "Device Energy Management (Matter 1.3)",
        0x0099: "EVSE Electric Vehicle Supply Equipment (Matter 1.3)",
    }

    endpoint = models.ForeignKey(
        MatterEndpoint,
        on_delete=models.CASCADE,
        related_name="clusters",
    )
    cluster_id = models.IntegerField()
    cluster_name = models.CharField(max_length=128)
    attributes = models.JSONField(
        default=dict,
        blank=True,
        help_text="Aktuelle Cluster-Attribute (z. B. active_power, on_off, energy)",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "matter"
        unique_together = ("endpoint", "cluster_id")
        verbose_name = "Matter Cluster"
        verbose_name_plural = "Matter Clusters"

    def __str__(self):
        return f"{self.endpoint} / Cluster {hex(self.cluster_id)} ({self.cluster_name})"

