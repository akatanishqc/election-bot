"""Pre-deployment validation checks."""

import os

REQUIRED_VARS = [
    "GEMINI_API_KEY",
    "PINECONE_API_KEY",
    "PINECONE_INDEX_NAME",
    "SUPABASE_URL",
    "SUPABASE_ANON_KEY",
    "ADMIN_SECRET_TOKEN",
]


def main() -> int:
    """Checks for required environment variables."""

    missing = [var for var in REQUIRED_VARS if not os.getenv(var)]

    if missing:
        print("Missing environment variables:")
        for var in missing:
            print(f"- {var}")
        return 1

    print("All required environment variables are set.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
