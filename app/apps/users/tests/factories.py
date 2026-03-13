import factory
from faker import Faker

from apps.users.models import User


fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.LazyAttribute(lambda _: fake.unique.email())
    username = factory.Sequence(lambda n: f"user_{n}")
    full_name = factory.LazyAttribute(lambda _: fake.name()[:100])
    is_verified = True

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        raw = extracted or "StrongPass123!"
        self.set_password(raw)
        if create:
            self.save()
