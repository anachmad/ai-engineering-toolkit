"""Phase 2 policy CLI: inspect, route and evaluate supplied evidence locally."""
import argparse
import json
import sys
from . import core


def main():
    parser = argparse.ArgumentParser(description='Inspect workflow routing and evaluate security evidence; never executes external skills')
    parser.add_argument('--config', help='Versioned JSON-formatted YAML policy')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('registry')
    risk = sub.add_parser('risk'); risk.add_argument('--factors', required=True, help='JSON object of boolean risk factors'); risk.add_argument('--profile', choices=('lean','standard','business-critical'))
    status = sub.add_parser('status'); status.add_argument('--host', choices=('codex','claude'), required=True); status.add_argument('--inventory', help='versioned JSON inventory of reviewed local installations')
    route = sub.add_parser('route'); route.add_argument('--intent', required=True); route.add_argument('--host', choices=('codex','claude'), required=True); route.add_argument('--risk', choices=core.RANK, required=True); route.add_argument('--inventory'); route.add_argument('--profile', choices=('lean','standard','business-critical'))
    gate = sub.add_parser('evaluate'); gate.add_argument('--stage', required=True); gate.add_argument('--risk', choices=core.RANK, required=True); gate.add_argument('--evidence', required=True, help='versioned JSON evidence file'); gate.add_argument('--host', choices=('codex','claude')); gate.add_argument('--inventory'); gate.add_argument('--profile', choices=('lean','standard','business-critical'))
    args = parser.parse_args()
    try:
        policy = core.policy(args.config)
        if args.command == 'registry': result = policy['skills']
        elif args.command == 'risk': result = core.classify(policy, json.loads(args.factors), args.profile)
        elif args.command == 'status':
            inventory = core.load(args.inventory).get('skills', {}) if args.inventory else {}
            result = [core.status(policy, x, args.host, inventory) for x in policy['skills']]
        elif args.command == 'route':
            inventory = core.load(args.inventory).get('skills', {}) if args.inventory else {}
            result = core.route(policy, args.intent, args.host, inventory, args.risk, args.profile)
        else:
            evidence = core.load(args.evidence)
            inventory = core.load(args.inventory).get('skills', {}) if args.inventory else {}
            result = core.evaluate(policy, args.risk, args.stage, evidence, host=args.host, inventory=inventory, profile=args.profile)
        print(json.dumps(result, indent=2))
        return 1 if isinstance(result,dict) and result.get('blocked') else 0
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        print(f'error: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
