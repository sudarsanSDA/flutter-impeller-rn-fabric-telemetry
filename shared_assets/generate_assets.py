"""Generates deterministic mock datasets and assets for cross-platform benchmarks."""

import datetime
import json
import os
import random
import uuid
from PIL import Image, ImageDraw


def generate_list_5k(output_path: str) -> None:
    """Generates 5,000 objects for list virtualization benchmarking."""
    random.seed(42)
    records = []
    for i in range(1, 5001):
        records.append({
            "id": i,
            "title": f"Item Title {i}",
            "subtitle": f"Secondary metadata description for item number {i}",
            "badge_count": random.randint(1, 99),
        })

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    print(f"Generated {output_path} with {len(records)} items.")


def generate_payload_10k(output_path: str) -> None:
    """Generates a ~5MB nested JSON document with 10,000 records for CPU parsing benchmarks."""
    random.seed(42)
    base_time = datetime.datetime(2026, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
    tag_pool = ["system", "telemetry", "metric", "network", "isolate", "render", "hermes", "impeller", "benchmark", "runtime"]
    categories = ["compute", "memory", "io", "graphics", "network"]

    records = []
    for _ in range(10000):
        random_seconds = random.randint(0, 31536000)
        record_time = base_time + datetime.timedelta(seconds=random_seconds)
        records.append({
            "guid": str(uuid.UUID(int=random.getrandbits(128), version=4)),
            "timestamp": record_time.isoformat(),
            "isActive": bool(random.getrandbits(1)),
            "description": "Benchmark telemetry payload record containing nested metrics and tags for deserialization and parsing analysis.",
            "tags": random.sample(tag_pool, 5),
            "metrics": {
                "score": round(random.uniform(10.0, 1000.0), 4),
                "count": random.randint(1, 10000),
                "category": random.choice(categories),
            },
        })

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"Generated {output_path} with {len(records)} items ({file_size_mb:.2f} MB).")


def generate_avatar(output_path: str) -> None:
    """Generates a 120x120 raw PNG asset rendered at 40x40dp."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    size = (120, 120)
    image = Image.new("RGBA", size, (240, 243, 246, 255))
    draw = ImageDraw.Draw(image)

    # Base background circle
    draw.ellipse([4, 4, 116, 116], fill=(59, 130, 246, 255), outline=(29, 78, 216, 255), width=2)
    # Head
    draw.ellipse([42, 24, 78, 60], fill=(255, 255, 255, 255))
    # Torso
    draw.chord([26, 66, 94, 126], start=180, end=0, fill=(255, 255, 255, 255))

    image.save(output_path, "PNG")
    print(f"Generated {output_path} (120x120 PNG).")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    images_dir = os.path.join(base_dir, "images")

    generate_list_5k(os.path.join(data_dir, "list_5k.json"))
    generate_payload_10k(os.path.join(data_dir, "payload_10k.json"))
    generate_avatar(os.path.join(images_dir, "avatar.png"))
