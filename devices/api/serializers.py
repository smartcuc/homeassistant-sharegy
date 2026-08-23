############################
# devices/api/serializers.py
############################

from rest_framework import serializers

from devices.models import (
    Device,
    DeviceConfig,
    DeviceRole,
    Room,
    Floor,
    Home,
    MQTTProfile,
    MetricDefinition,
)

from energy.models import (
    EMSSignalSource,
    EMSSignalType,
)

from producer.models import GeneratorType

# ============================================================
# ✅ ROLE
# ============================================================

class DeviceRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceRole
        fields = ("id", "key", "label")


# ============================================================
# ✅ LOCATION
# ============================================================

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ("id", "name")


class FloorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Floor
        fields = ("id", "name")


# ============================================================
# ✅ CONFIG
# ============================================================

class DeviceConfigSerializer(serializers.ModelSerializer):

    display_name = serializers.CharField(
            source="name",
            required=False,
            allow_blank=True,
        )

    # READ
    role = DeviceRoleSerializer(read_only=True)
    room = RoomSerializer(read_only=True)
    floor = FloorSerializer(read_only=True)
    generator_type = serializers.SerializerMethodField()
    metric_definition = serializers.SerializerMethodField()
    energy_signal_type = serializers.SerializerMethodField()

    # WRITE
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=DeviceRole.objects.all(),
        source="role",
        write_only=True,
        allow_null=True,
        required=False
    )

    generator_type_id = serializers.PrimaryKeyRelatedField(
        queryset=GeneratorType.objects.all(),
        source="generator_type",
        write_only=True,
        allow_null=True,
        required=False,
    )

    metric_definition_id = serializers.PrimaryKeyRelatedField(
        queryset=MetricDefinition.objects.all(),
        source="metric_definition",
        write_only=True,
        allow_null=True,
        required=False,
    )

    energy_signal_type_id = serializers.PrimaryKeyRelatedField(
        queryset=EMSSignalType.objects.all(),
        source="energy_signal_type",
        required=False,
    )

    room_id = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.all(),
        source="room",
        write_only=True,
        allow_null=True,
        required=False
    )

    floor_id = serializers.PrimaryKeyRelatedField(
        queryset=Floor.objects.all(),
        source="floor",
        write_only=True,
        allow_null=True,
        required=False
    )

    home_id = serializers.PrimaryKeyRelatedField(
        queryset=Home.objects.all(),
        source="home",
        write_only=True,
        allow_null=True,
        required=False
    )

    class Meta:
        model = DeviceConfig

        fields = (
            "display_name",
            "role",
            "role_id",
            "generator_type",
            "generator_type_id",
            "metric_definition",
            "metric_definition_id",
            "energy_signal_type",
            "energy_signal_type_id",
            "room",
            "room_id",
            "floor",
            "floor_id",
            "home_id",
        )

    # ✅ ✅ ✅ HIER IST DER FIX
    def validate(self, data):

        request = self.context.get("request")
        user = request.user if request else None

        # ✅ FIELD EXISTENZ prüfen (WICHTIG)
        if "home" in data:
            home = data["home"]

            # ❌ explizit null → NICHT erlauben
            if home is None:
                # stattdessen aktuelles behalten
                home = getattr(self.instance, "home", None)
        else:
            # nicht gesendet → aktuelles behalten
            home = getattr(self.instance, "home", None)

        # ✅ fallback: user default
        if not home and user:
            home = user.homes.first()

        # 🚨 FINAL GUARANTEE
        if not home:
            raise serializers.ValidationError("Kein Zuhause verfügbar")

        data["home"] = home

        return data

    def update(self, instance, validated_data):

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        EMSSignalSource.objects.filter(
            device=instance.device
        ).delete()

        if instance.energy_signal_type and instance.energy_signal_type.key != "none":

            EMSSignalSource.objects.create(
                home=instance.home,
                device=instance.device,
                signal_type=instance.energy_signal_type,
            )

        return instance

    def get_generator_type(self, obj):

        if not obj.generator_type:
            return None

        return {
            "id": obj.generator_type.id,
            "key": obj.generator_type.key,
            "name": obj.generator_type.name,
            "icon": obj.generator_type.icon,
        }

    def get_metric_definition(self, obj):

        if not obj.metric_definition:
            return None

        return {
            "id": obj.metric_definition.id,
            "key": obj.metric_definition.key,
            "name": obj.metric_definition.name,
            "unit": obj.metric_definition.unit,
        }

    def get_energy_signal_type(self, obj):

        if not obj.energy_signal_type:
            return None

        return {
            "id": obj.energy_signal_type.id,
            "key": obj.energy_signal_type.key,
            "label": obj.energy_signal_type.label,
        }


# ============================================================
# ✅ DEVICE
# ============================================================

class DeviceSerializer(serializers.ModelSerializer):

    config = DeviceConfigSerializer(read_only=True)

    display_name = serializers.SerializerMethodField()
    classified = serializers.SerializerMethodField()

    last_seen = serializers.DateTimeField(
        read_only=True,
        allow_null=True,
    )

    delete_after = serializers.DateTimeField(
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = Device
        
        fields = (
            "id",
            "identifier",
            "display_name",
            "classified",
            "last_seen",
            "delete_after",
            "config",
        )

    def get_display_name(self, obj):
        if hasattr(obj, "config") and obj.config:
            return obj.config.display_name()
        return obj.identifier

    def get_classified(self, obj):
        if hasattr(obj, "config") and obj.config:
            return obj.config.is_classified()
        return False


# ============================================================
# ✅ DEVICE
# ============================================================

class HomeSerializer(serializers.ModelSerializer):
    mqtt_host = serializers.SerializerMethodField()
    mqtt_port = serializers.SerializerMethodField()

    class Meta:
        model = Home
        fields = (
            "id",
            "name",
            "timezone",
            "postal_code",
            "city",
            "mqtt_token",
            "mqtt_username",
            "mqtt_password",
            "mqtt_host",
            "mqtt_port",
            "created_at",
        )

    def get_mqtt_host(self, obj):
        import os
        return os.getenv("MQTT_HOST", "mqtt.sharegy.de")

    def get_mqtt_port(self, obj):
        import os
        return int(os.getenv("MQTT_PORT", 1883))


class MQTTProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MQTTProfile
        fields = [
            "id",
            "slug",
            "name",
        ]
