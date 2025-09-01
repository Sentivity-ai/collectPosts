import argparse
import sys
import json
from api_client import CollectPostsAPI

def main():
    parser = argparse.ArgumentParser(
        description="CollectPosts API CLI - Simple one-line commands",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py scrape "politics" --limit 100
  python cli.py hashtags --posts-file posts.json --max 20
  python cli.py hive --posts-file posts.json
  python cli.py upload --posts-file posts.json --repo "username/repo"
  python cli.py health
        """
    )
    
    parser.add_argument('--url', default=None, 
                       help='Your Render service URL (or set COLLECTPOSTS_URL env var)')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    scrape_parser = subparsers.add_parser('scrape', help='Scrape social media posts')
    scrape_parser.add_argument('query', help='Search query (e.g., "politics", "tech")')
    scrape_parser.add_argument('--sources', nargs='+', 
                              choices=['reddit', 'youtube', 'instagram'],
                              default=['reddit', 'youtube', 'instagram'],
                              help='Sources to scrape')
    scrape_parser.add_argument('--limit', type=int, default=100, 
                              help='Maximum posts per source')
    scrape_parser.add_argument('--days', type=int, default=30, 
                              help='Lookback period in days')
    scrape_parser.add_argument('--output', help='Output file for results (JSON)')
    
    hashtags_parser = subparsers.add_parser('hashtags', help='Generate hashtags from posts')
    hashtags_parser.add_argument('--posts-file', required=True, 
                                help='JSON file containing posts')
    hashtags_parser.add_argument('--max', type=int, default=50, 
                                help='Maximum number of hashtags')
    hashtags_parser.add_argument('--output', help='Output file for hashtags (JSON)')
    
    hive_parser = subparsers.add_parser('hive', help='Process posts for Hive')
    hive_parser.add_argument('--posts-file', required=True, 
                            help='JSON file containing posts')
    hive_parser.add_argument('--hive-url', help='Custom Hive service URL')
    hive_parser.add_argument('--output', help='Output file for results (JSON)')
    
    upload_parser = subparsers.add_parser('upload', help='Upload posts to Hugging Face')
    upload_parser.add_argument('--posts-file', required=True, 
                              help='JSON file containing posts')
    upload_parser.add_argument('--repo', required=True, 
                              help='HF repository name (username/repo)')
    upload_parser.add_argument('--hf-token', help='Hugging Face token')
    upload_parser.add_argument('--output', help='Output file for results (JSON)')
    
    subparsers.add_parser('health', help='Check service health')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    api = CollectPostsAPI(args.url)
    
    try:
        if args.command == 'scrape':
            print(f"Scraping '{args.query}' from {', '.join(args.sources)}...")
            result = api.scrape(args.query, args.sources, args.limit, args.days)
            
            if "error" in result:
                print(f"Error: {result['error']}")
                sys.exit(1)
            
            posts = result.get('all_posts', [])
            print(f"Found {len(posts)} posts")
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"Results saved to {args.output}")
            else:
                print(json.dumps(result, indent=2))
        
        elif args.command == 'hashtags':
            print(f"Generating hashtags...")
            with open(args.posts_file, 'r') as f:
                posts = json.load(f)
            
            hashtags = api.get_hashtags(posts, args.max)
            print(f"Generated {len(hashtags)} hashtags")
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump({"hashtags": hashtags}, f, indent=2)
                print(f"Hashtags saved to {args.output}")
            else:
                print(json.dumps({"hashtags": hashtags}, indent=2))
        
        elif args.command == 'hive':
            print(f"Processing for Hive...")
            with open(args.posts_file, 'r') as f:
                posts = json.load(f)
            
            result = api.process_for_hive(posts, args.hive_url)
            print(f"Hive processing completed")
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"Results saved to {args.output}")
            else:
                print(json.dumps(result, indent=2))
        
        elif args.command == 'upload':
            print(f"Uploading to Hugging Face...")
            with open(args.posts_file, 'r') as f:
                posts = json.load(f)
            
            result = api.upload_to_hf(posts, args.repo, args.hf_token)
            print(f"Upload completed")
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"Results saved to {args.output}")
            else:
                print(json.dumps(result, indent=2))
        
        elif args.command == 'health':
            print("Checking service health...")
            if api.health_check():
                print("Service is healthy and running")
            else:
                print("Service is down or unreachable")
                sys.exit(1)
    
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
