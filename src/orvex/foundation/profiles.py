"""Profile identity and service-side age policy. PIN authentication is deliberately unavailable."""

from typing import Protocol
from uuid import uuid4
from .models import Profile, valid_age, utc_now


class AuthenticationUnavailable(PermissionError):
    pass


class AdultAuthorizer(Protocol):
    def require(self, profile_id: str, scope: str, proof: object) -> None:
        """Validate an authentic, scoped, expiring proof or raise PermissionError."""
        ...


class NoPinAuthorizer:
    def require(self, profile_id, scope, proof):
        raise AuthenticationUnavailable(
            "Autenticación PIN todavía no implementada; operación protegida bloqueada."
        )


class ProfileService:
    def __init__(self, repository, authorizer=None):
        self.repo = repository
        self.authorizer = authorizer or NoPinAuthorizer()

    def get(self, profile_id):
        row = self.repo.profile(profile_id)
        if not row or not row["enabled"]:
            raise PermissionError("Perfil no disponible.")
        return Profile(row["id"], row["kind"], row["name"], row["max_age"], bool(row["enabled"]))

    def list_profiles(self, actor_id):
        actor = self.get(actor_id)
        if actor.kind == "child":
            return [actor]
        return [self.get(row["id"]) for row in self.repo.profiles()]

    def require_adult(self, profile_id):
        profile = self.get(profile_id)
        if profile.kind != "adult":
            raise PermissionError("Operación disponible en el perfil adulto.")
        return profile

    def create(self, actor_id, name, kind, max_age=None, proof=None):
        self.require_adult(actor_id)
        self.authorizer.require(actor_id, "manage_profiles", proof)
        if (
            kind not in ("adult", "child")
            or not isinstance(name, str)
            or not name.strip()
            or len(name) > 100
        ):
            raise ValueError("Nombre o tipo de perfil no válido.")
        if kind == "child" and not valid_age(max_age, 17):
            raise ValueError("Edad infantil no válida.")
        if kind == "adult" and max_age is not None:
            raise ValueError("Un adulto no tiene límite infantil.")
        profile_id = "profile-" + uuid4().hex
        self.repo.create_profile(
            profile_id, kind, name.strip(), int(max_age) if max_age is not None else None, utc_now()
        )
        return self.get(profile_id)

    @staticmethod
    def allows(profile, content):
        if not profile.enabled:
            return False
        if profile.kind == "adult":
            return True
        return (
            profile.kind == "child"
            and valid_age(profile.max_age, 17)
            and valid_age(content.age, profile.max_age)
        )
