import json
import orjson
import sys
from optimized_json import FastCachedJSONEncoder
import pyperf


EMPTY = ({}, 2000)
SIMPLE_DATA = {'key1': 0, 'key2': True, 'key3': 'value', 'key4': 'foo',
               'key5': 'string'}
SIMPLE = (SIMPLE_DATA, 1000)
NESTED_DATA = {'key1': 0, 'key2': SIMPLE[0], 'key3': 'value', 'key4': SIMPLE[0],
               'key5': SIMPLE[0], 'key': '\u0105\u0107\u017c'}
NESTED = (NESTED_DATA, 1000)
HUGE = ([NESTED[0]] * 1000, 1)

UNICODE_HEAVY_DATA =  {
    "chinese_simplified": "这是中文内容，包含汉字和标点符号。我们正在测试JSON性能优化技术。" * 50,
    "chinese_traditional": "這是繁體中文內容，測試JSON編碼效能。包含複雜漢字結構和語法。" * 50,
    "arabic": "هذا محتوى عربي يحتوي على نصوص وعلامات ترقيم مختلفة لاختبار الأداء." * 50,
    "hebrew": "זה תוכן בעברית הכולל אותיות וסימני פיסוק שונים לבדיקת ביצועים." * 50,
    "russian": "Это русский текст с кириллическими символами для тестирования производительности JSON." * 50,
    "japanese_hiragana": "これはひらがなのテキストです。JSONのパフォーマンステストに使用されています。" * 40,
}
UNICODE_HEAVY = (UNICODE_HEAVY_DATA, 1000)

CASES = ['EMPTY', 'SIMPLE', 'NESTED', 'HUGE', 'UNICODE_HEAVY']

def create_simple_repetitive_data():
    """
    Create simple but highly repetitive data that maximally benefits from caching.
    
    Strategy: Create a few large shared objects and reference them extensively.
    """
    
    # One large shared configuration object
    shared_config = {
        "database_settings": {
            "host": "production-db.company.com",
            "port": 5432,
            "username": "app_user",
            "ssl_enabled": True,
            "connection_pool": {
                "min_connections": 10,
                "max_connections": 100,
                "idle_timeout_seconds": 600,
                "connection_lifetime_seconds": 3600,
                "validation_query": "SELECT 1",
                "retry_attempts": 3,
                "retry_delay_ms": 1000
            },
            "performance_tuning": {
                "query_timeout_seconds": 30,
                "slow_query_threshold_ms": 1000,
                "enable_query_cache": True,
                "cache_size_mb": 256,
                "statistics_enabled": True,
                "logging_slow_queries": True
            },
            "backup_settings": {
                "enabled": True,
                "schedule": "0 2 * * *",
                "retention_days": 30,
                "compression_enabled": True,
                "encryption_enabled": True,
                "backup_location": "/backups/database",
                "verify_backup_integrity": True
            }
        },
        "cache_settings": {
            "redis_cluster": [
                {"host": "redis-1.company.com", "port": 6379, "role": "master"},
                {"host": "redis-2.company.com", "port": 6379, "role": "replica"},
                {"host": "redis-3.company.com", "port": 6379, "role": "replica"}
            ],
            "default_ttl_seconds": 3600,
            "max_memory_mb": 2048,
            "eviction_policy": "allkeys-lru",
            "persistent_storage": True,
            "compression_enabled": True,
            "security": {
                "password_required": True,
                "ssl_enabled": True,
                "client_certificate_required": False
            }
        },
        "logging_configuration": {
            "level": "INFO",
            "format": "json",
            "include_stack_trace": True,
            "max_file_size_mb": 100,
            "max_files": 10,
            "log_rotation_enabled": True,
            "destinations": [
                {"type": "file", "path": "/logs/application.log"},
                {"type": "stdout", "enabled": True},
                {"type": "elasticsearch", "endpoint": "https://logs.company.com:9200"}
            ],
            "structured_logging": {
                "include_timestamp": True,
                "include_correlation_id": True,
                "include_user_id": True,
                "include_request_id": True,
                "include_session_id": True
            }
        }
    }
    
    # One shared user object
    shared_user = {
        "user_id": "user_12345",
        "username": "john.smith@company.com",
        "display_name": "John Smith",
        "employee_id": "EMP2024001",
        "department": "Engineering",
        "team": "Platform Infrastructure",
        "role": "Senior Software Engineer",
        "manager": "sarah.johnson@company.com",
        "permissions": [
            "read:all_repositories",
            "write:own_repositories", 
            "deploy:staging_environment",
            "access:production_logs",
            "manage:infrastructure_configs",
            "approve:code_reviews",
            "access:database_readonly",
            "manage:ci_cd_pipelines"
        ],
        "profile": {
            "email": "john.smith@company.com",
            "phone": "+1-555-123-4567",
            "office_location": "Building A, Floor 5, Desk 42",
            "start_date": "2022-01-15",
            "timezone": "America/Los_Angeles",
            "preferred_language": "en-US"
        },
        "settings": {
            "notifications": {
                "email_enabled": True,
                "slack_enabled": True,
                "mobile_push_enabled": False,
                "weekly_digest": True
            },
            "ui_preferences": {
                "theme": "dark",
                "sidebar_collapsed": False,
                "items_per_page": 50,
                "default_dashboard": "overview"
            }
        }
    }
    
    # Now create data structure that references these objects hundreds of times
    massive_repetitive_data = {
        "system_overview": {
            "total_services": 200,
            "global_config": shared_config,    # Reference 1
            "system_admin": shared_user,       # Reference 1
            "default_settings": shared_config  # Reference 2
        },
        "services": [],
        "audit_trail": [],
        "user_sessions": []
    }
    
    # Create 200 services, each referencing the same config and user
    for i in range(200):
        service = {
            "service_id": f"service_{i:03d}",
            "name": f"microservice-{i:03d}",
            "config": shared_config,        # Reference 3, 4, 5... 202
            "owner": shared_user,           # Reference 2, 3, 4... 201  
            "runtime_config": shared_config, # Reference 203, 204... 402
            "last_deployed_by": shared_user  # Reference 202, 203... 401
        }
        massive_repetitive_data["services"].append(service)
    
    # Create 300 audit entries, each referencing the same user and config
    for i in range(300):
        audit_entry = {
            "audit_id": f"audit_{i:04d}",
            "timestamp": "2024-09-01T10:00:00Z",
            "action": f"action_{i % 10}",  # Some variety
            "user": shared_user,           # Reference 402, 403... 701
            "affected_config": shared_config, # Reference 403, 404... 702
            "performed_by": shared_user,   # Reference 702, 703... 1001
            "context": {
                "config_snapshot": shared_config, # Reference 703, 704... 1002
                "user_context": shared_user       # Reference 1002, 1003... 1301
            }
        }
        massive_repetitive_data["audit_trail"].append(audit_entry)
    
    # Create 100 user sessions, all for the same user with same config
    for i in range(100):
        session = {
            "session_id": f"session_{i:03d}",
            "user": shared_user,           # Reference 1302, 1303... 1401
            "config": shared_config,       # Reference 1003, 1004... 1102
            "preferences": shared_user,    # Reference 1402, 1403... 1501 (reusing user as preferences)
            "system_settings": shared_config # Reference 1103, 1104... 1202
        }
        massive_repetitive_data["user_sessions"].append(session)
    
    # Add some top-level references for even more repetition
    massive_repetitive_data["global_user"] = shared_user      # Reference 1502
    massive_repetitive_data["global_config"] = shared_config  # Reference 1203
    massive_repetitive_data["backup_config"] = shared_config  # Reference 1204
    massive_repetitive_data["admin_user"] = shared_user       # Reference 1503
    
    return massive_repetitive_data


def bench_json_dumps(data):
    for obj, count_it in data:
        for _ in count_it:
            json.dumps(obj)

def bench_json_dumps_opt(data):
    encoder = FastCachedJSONEncoder(separators=(',', ':'), ensure_ascii=False)
    for obj, count_it in data:
        for _ in count_it:
            encoder.encode(obj)

def bench_orjson_dumps(data):
    for obj, count_it in data:
        for _ in count_it:
            orjson.dumps(obj)

OPT_LEVELS = {"0" : bench_json_dumps, "1" : bench_json_dumps_opt, "2" : bench_orjson_dumps}


def add_cmdline_args(cmd, args):
    if args.cases:
        cmd.extend(("--cases", args.cases))
    if args.opt_level:
        cmd.extend(("--opt_level", args.opt_level))


def main():
    runner = pyperf.Runner(add_cmdline_args=add_cmdline_args)
    runner.argparser.add_argument("--cases",
                                  help="Comma separated list of cases. Available cases: %s. By default, run all cases."
                                       % ', '.join(CASES))
    runner.argparser.add_argument("--opt_level",
                                  help="Level of optimization. Available cases: %s. By default, run unoptimized."
                                       % ', '.join(list(OPT_LEVELS.keys())))
    runner.metadata['description'] = "Benchmark json.dumps()"

    args = runner.parse_args()
    if args.cases:
        cases = []
        for case in args.cases.split(','):
            case = case.strip()
            if case:
                cases.append(case)
        if not cases:
            print("ERROR: empty list of cases")
            sys.exit(1)
    else:
        cases = CASES

    bench_function = bench_json_dumps
    if args.opt_level:
        assert args.opt_level in OPT_LEVELS, f"{args.opt_level} is not a valid argument"
        bench_function = OPT_LEVELS[args.opt_level]

    data = []
    for case in cases:
        obj, count = globals()[case]
        data.append((obj, range(count)))
    data.append((create_simple_repetitive_data(), range(10)))
    runner.bench_func('json_dumps', bench_function, data)


if __name__ == '__main__':
    main()