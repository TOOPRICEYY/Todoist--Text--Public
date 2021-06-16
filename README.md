Software that syncs text file task management with Todoist

Text file format -> line starting with ' indicates a task,  "- done" on the end of the line is interpreted as a complete task
The date on the text file is used as the date of the task in mm - dd - yy


All Configuration performed in .conf file created in dbmanage.py root directory

Run service with "python3 dbmanage.py -p {insert pid file here}"

.conf format:
```
db_loc:{location to store json database}
temp_loc:{location to store temp active directory from nextcloud}
todoist_api_key:{api key for nextcloud}
nextcloud_link:{server link for nextcloud}
nextcloud_user:{username for nextcloud}
nextcloud_pass:{password for nextcloud}
refresh_int:{how often to check for file updates in seconds}
log_loc:{where to log errors}
days_primed:{insert days to automatically create note files for}
last_day_to_sync:{oldest todoist tasks to sync, implimeted to prevent vistigal tasks hanging around after clearing text file side}
