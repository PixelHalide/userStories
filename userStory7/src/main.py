from pathlib import Path

from userStory7.src.mapper import save_mapped_output


def main() -> None:
    story_dir = Path(__file__).resolve().parents[1]
    output_path = save_mapped_output(
        story_dir / "data" / "raw_data.csv",
        story_dir / "data" / "reference_data.xlsx",
        story_dir / "output" / "mapped_output.csv",
    )
    print(f"Mapped output saved to {output_path}")


if __name__ == "__main__":
    main()
