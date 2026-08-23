########################
# devices/serializers.py
########################

from rest_framework import serializers
from .models import Device, Home, MQTTProfile

from devices.tasks import provision_home
from devices.api.serializers import DeviceConfigSerializer
from devices.services.device_health import device_status


# ✅ READ SERIALIZER (für Dashboard etc.)
class DeviceSerializer(serializers.ModelSerializer):

    config = serializers.SerializerMethodField()

    display_name = serializers.SerializerMethodField()

    class Meta:
        model = Device
        fields = [
            "id",
            "identifier",
            "display_name",
            "configured",
            "last_seen",
            "delete_after",
            "config",
        ]

    def get_display_name(self, obj):
        if hasattr(obj, "config") and obj.config:
            return obj.config.display_name()
        return obj.identifier

    def get_config(self, obj):
        if hasattr(obj, "config") and obj.config:
            return DeviceConfigSerializer(obj.config).data
        return None


# ✅ CREATE SERIALIZER (für POST /api/devices/)
class DeviceCreateSerializer(serializers.ModelSerializer):

    identifier = serializers.CharField()
    name = serializers.CharField(required=False, allow_blank=True)

    mqtt_profile = serializers.PrimaryKeyRelatedField(
        queryset=MQTTProfile.objects.filter(active=True),
        required=False,
        allow_null=True,
    )

    role_id = serializers.IntegerField(required=False, allow_null=True)
    role_key = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    generator_type_id = serializers.IntegerField(required=False, allow_null=True)
    generator_type_key = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    metric_definition_id = serializers.IntegerField(required=False, allow_null=True)
    metric_key = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    energy_signal_type_id = serializers.IntegerField(required=False, allow_null=True)
    energy_signal_type_key = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    room_id = serializers.IntegerField(required=False, allow_null=True)
    floor_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Device
        fields = [
            "identifier",
            "name",
            "mqtt_profile",
            "role_id",
            "role_key",
            "generator_type_id",
            "generator_type_key",
            "metric_definition_id",
            "metric_key",
            "energy_signal_type_id",
            "energy_signal_type_key",
            "room_id",
            "floor_id",
        ]

    def create(self, validated_data):
        user = self.context["request"].user

        # ✅ Home holen oder erstellen
        home = user.homes.first()
        created = False

        if not home:
            home = Home.objects.create(
                user=user,
                name="Mein Zuhause"
            )
            created = True

        identifier = validated_data["identifier"]
        name = validated_data.get("name")
        mqtt_profile = validated_data.get("mqtt_profile")

        device, created = Device.objects.get_or_create(
            home=home,
            identifier=identifier,
            defaults={
                "active": True,
                "pending_delete": False,
                "mqtt_profile": mqtt_profile,
            },
        )

        if not created:
            device.active = True
            device.pending_delete = False
            device.delete_after = None
            if mqtt_profile:
                device.mqtt_profile = mqtt_profile

            device.save(
                update_fields=[
                    "active",
                    "pending_delete",
                    "delete_after",
                    "mqtt_profile",
                ]
            )

        # ✅ DeviceConfig anlegen / aktualisieren
        from devices.models import DeviceConfig, DeviceRole, MetricDefinition, Room, Floor
        from producer.models import GeneratorSystem, GeneratorType
        from energy.models import EMSSignalType

        config, _ = DeviceConfig.objects.get_or_create(
            device=device,
            defaults={"home": home}
        )

        if name:
            config.name = name

        # Rolle
        role_id = validated_data.get("role_id")
        role_key = validated_data.get("role_key")
        if role_id:
            config.role_id = role_id
        elif role_key:
            role_obj = DeviceRole.objects.filter(key=role_key).first()
            if role_obj:
                config.role = role_obj

        # Generator Type
        gen_id = validated_data.get("generator_type_id")
        gen_key = validated_data.get("generator_type_key")
        if gen_id:
            config.generator_type_id = gen_id
        elif gen_key:
            gen_obj = GeneratorType.objects.filter(key=gen_key, active=True).first()
            if gen_obj:
                config.generator_type = gen_obj

        # Metric Definition
        metric_id = validated_data.get("metric_definition_id")
        metric_key = validated_data.get("metric_key")
        if metric_id:
            config.metric_definition_id = metric_id
        elif metric_key:
            m_obj = MetricDefinition.objects.filter(key=metric_key).first()
            if m_obj:
                config.metric_definition = m_obj

        # Energy Signal Type
        sig_id = validated_data.get("energy_signal_type_id")
        sig_key = validated_data.get("energy_signal_type_key")
        if sig_id:
            config.energy_signal_type_id = sig_id
        elif sig_key:
            sig_obj = EMSSignalType.objects.filter(key=sig_key, active=True).first()
            if sig_obj:
                config.energy_signal_type = sig_obj

        # Room & Floor
        room_id = validated_data.get("room_id")
        floor_id = validated_data.get("floor_id")
        if room_id:
            config.room_id = room_id
        if floor_id:
            config.floor_id = floor_id

        config.save()

        # Producer System synchronisieren
        if (
            config.role
            and config.role.key == "producer"
            and config.generator_type
        ):
            GeneratorSystem.objects.get_or_create(
                device=device,
                defaults={
                    "home": home,
                    "name": config.display_name(),
                    "generator_type": config.generator_type,
                },
            )

        device.configured = config.is_classified()
        device.save(update_fields=["configured"])

        if created:
            provision_home.delay(home.id)

        return device


# ✅ STATUS SERIALIZER (für Monitoring)
class DeviceStatusSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    last_seen = serializers.DateTimeField(allow_null=True)
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = Device
        fields = [
            "id",
            "identifier",
            "display_name",
            "status",
            "last_seen",
        ]

    def get_status(self, obj):
        return device_status(obj)

    def get_display_name(self, obj):
        if hasattr(obj, "config") and obj.config:
            return obj.config.display_name()
        return obj.identifier
    
    