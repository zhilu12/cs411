from typing import Any

from wildlife_tracker.migration_tracking.migration_path import MigrationPath

class Migration:
    def __init__(self,
                 migration_id: int,
                 current_location: str,
                 migration_path: MigrationPath,
                 start_date: str,
                 status: str = "Scheduled",
                 current_date: str) -> None:
        self.migration_id = migration_id
        self.current_location = current_location
        self.migration_path = migration_path
        self.start_date = start_date
        self.status = status
        self.current_date = current_date

    
    def cancel_migration(migration_id: int) -> None:
        pass

    def get_migration_details(migration_id: int) -> dict[str, Any]:
        pass

    def update_migration_details(migration_id: int, **kwargs: Any) -> None:
        pass 

