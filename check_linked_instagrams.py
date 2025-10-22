#!/usr/bin/env python3
"""
Utility: List Instagram Business Accounts linked to a Facebook user or page

Usage:
  - Set an access token in env: REACT_APP_ACCESS_TOKEN or FB_ACCESS_TOKEN
  - Run: python3 backinsta/check_linked_instagrams.py --facebook-id me

Notes:
  - Token must have permissions to read pages (pages_read_engagement / pages_show_list)
  - For best results use a long-lived token or a Page access token
"""

import os
import sys
import argparse
import requests
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

GRAPH_API_BASE = "https://graph.facebook.com/v18.0"


def get_token() -> Optional[str]:
    return os.getenv('FB_ACCESS_TOKEN') or os.getenv('REACT_APP_ACCESS_TOKEN') or os.getenv('ACCESS_TOKEN')


def fetch_pages(user_id: str, token: str):
    """Fetch Facebook Pages for a user or the given id"""
    url = f"{GRAPH_API_BASE}/{user_id}/accounts"
    params = {'access_token': token}
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def fetch_page_instagram(page_id: str, token: str):
    """Fetch instagram_business_account field for a page"""
    url = f"{GRAPH_API_BASE}/{page_id}"
    params = {
        'fields': 'id,name,instagram_business_account{username,id,profile_picture_url}',
        'access_token': token
    }
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def pretty_print_linked(accounts_json, user_id: str):
    data = accounts_json.get('data', []) if isinstance(accounts_json, dict) else []
    if not data:
        print(f"No Facebook Pages found for '{user_id}'.")
        return

    print(f"Found {len(data)} Facebook Page(s) for '{user_id}':\n")
    for page in data:
        page_id = page.get('id')
        page_name = page.get('name')
        page_access_token = page.get('access_token')
        print(f"Page: {page_name} (id: {page_id})")

        # Try to fetch instagram business account using page-level token if available
        token_to_use = page_access_token or get_token()
        try:
            page_info = fetch_page_instagram(page_id, token_to_use)
            ig = page_info.get('instagram_business_account')
            if ig:
                print("  -> Instagram Business Account linked:")
                print(f"       id: {ig.get('id')}")
                print(f"       username: {ig.get('username')}")
                print(f"       profile_picture_url: {ig.get('profile_picture_url')}")
            else:
                print("  -> No Instagram Business Account linked to this Page")
        except requests.HTTPError as e:
            print(f"  -> Error fetching IG info for page {page_id}: {e}")
        except Exception as e:
            print(f"  -> Unexpected error: {e}")


def main(argv=None):
    parser = argparse.ArgumentParser(description='List Instagram Business Accounts linked to a Facebook user/page')
    parser.add_argument('--facebook-id', '-f', default='me', help="Facebook Graph ID or 'me' (default: me)")
    args = parser.parse_args(argv)

    token = get_token()
    if not token:
        print("ERROR: No access token found. Set REACT_APP_ACCESS_TOKEN or FB_ACCESS_TOKEN in the environment.")
        sys.exit(2)

    facebook_id = args.facebook_id

    try:
        pages = fetch_pages(facebook_id, token)
    except requests.HTTPError as e:
        print(f"Failed to fetch pages for '{facebook_id}': {e}\nResponse: {getattr(e.response, 'text', '')}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error fetching pages: {e}")
        sys.exit(1)

    pretty_print_linked(pages, facebook_id)


if __name__ == '__main__':
    main()
