# fix_fixture.py
import json
import sys

# Load the JSON data from standard input
try:
    data = json.load(sys.stdin)
except json.JSONDecodeError as e:
    print(f"Error decoding JSON: {e}", file=sys.stderr)
    sys.exit(1)

user_map = {}
player_users_seen = set()
cleaned_data = []

# --- Pass 1: Build the username-to-ID map ---
for obj in data:
    # Assuming 'auth.user' or a similar model defines the primary keys (IDs)
    if obj.get('model') == 'auth.user':
        username = obj['fields']['username'] # Assumes username is correct field
        user_map[username] = obj['pk']

# --- Pass 2: Clean and Reformat Data ---
for obj in data:
    if obj.get('model') == 'quiz_site.player':
        fields = obj.get('fields', {})
        user_field = fields.get('user')

        # Check for the incorrect format: ["username"]
        if isinstance(user_field, list) and len(user_field) == 1 and isinstance(user_field[0], str):
            username = user_field[0]
            
            # 1. FIX THE FORMAT: Get the ID from the map
            if username in user_map:
                user_id = user_map[username]
                obj['fields']['user'] = user_id # Corrected to integer ID

                # 2. FIX THE DUPLICATE ERROR: Check if we've seen this user ID already
                if user_id in player_users_seen:
                    # Skip this entry to fix the "Key (user_id)=(4) already exists" error
                    print(f"Skipping duplicate player entry for user ID {user_id} ({username})", file=sys.stderr)
                    continue
                else:
                    player_users_seen.add(user_id)
            else:
                print(f"Warning: Could not find user ID for username '{username}'. Skipping player entry.", file=sys.stderr)
                continue

    # Add the cleaned object (or non-player object) to the new list
    cleaned_data.append(obj)

# Output the cleaned data as a single-line JSON fixture
json.dump(cleaned_data, sys.stdout)
print(file=sys.stdout) # Ensure a final newline
