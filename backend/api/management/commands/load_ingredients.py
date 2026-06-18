import json
from pathlib import Path

from django.core.management.base import BaseCommand

from api.models import Ingredient


class Command(BaseCommand):
    help = "Load ingredients from JSON."

    def add_arguments(self, parser):
        parser.add_argument(
            "path",
            nargs="?",
            default="/app/data/ingredients.json",
        )

    def handle(self, *args, **options):
        path = Path(options["path"])
        if not path.exists():
            local_path = (
                Path(__file__).resolve().parents[4]
                / "data"
                / "ingredients.json"
            )
            path = local_path if local_path.exists() else path
        if not path.exists():
            self.stdout.write(self.style.WARNING(f"File not found: {path}"))
            return
        with path.open(encoding="utf-8") as file:
            data = json.load(file)
        ingredients = [
            Ingredient(
                name=item["name"],
                measurement_unit=item["measurement_unit"],
            )
            for item in data
        ]
        Ingredient.objects.bulk_create(
            ingredients,
            ignore_conflicts=True,
        )
        self.stdout.write(self.style.SUCCESS("Ingredients loaded."))
