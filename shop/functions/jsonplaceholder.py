import requests


def get_jsonplaceholder_posts(user_id=None):
    """Fetch posts from JSONPlaceholder, optionally filtered by user ID."""

    url = "https://jsonplaceholder.typicode.com/posts"

    params = {}

    if user_id is not None:
        params["userId"] = user_id

    try:
        response = requests.get(url, params=params)

        if response.status_code != 200:
            print("Failed to fetch posts.")
            return None

        data = response.json()

        posts = []

        for post in data:
            posts.append(
                {
                    "id": post["id"],
                    "title": post["title"],
                    "body": post["body"],
                    "userId": post["userId"],
                }
            )

        return posts

    except requests.RequestException:
        print("Could not connect to JSONPlaceholder.")
        return None
