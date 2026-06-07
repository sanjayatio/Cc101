from gfl2.patterns.weekly_gunsmoke import parse as parse_weekly_gunsmoke
from gfl2.patterns.daily_gunsmoke import parse as parse_daily_gunsmoke
from gfl2.patterns.daily_gunsmoke import ReportEntry

PATTERNS = {
    "weekly_gunsmoke": parse_weekly_gunsmoke,
    "daily_gunsmoke":  parse_daily_gunsmoke,
}
