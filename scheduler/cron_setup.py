from crontab import CronTab
import getpass
import os

def setup_cron_job(script_path: str, schedule: str = "0 * * * *", comment: str = "weather_forecast_hourly"):
    """
    Create a cron job that runs the given script at the specified schedule.
    Default: every hour on the hour.
    """
    user = getpass.getuser()
    cron = CronTab(user=user)

    # Remove existing job with the same comment
    cron.remove_all(comment=comment)

    # Add new job
    job = cron.new(command=f"{os.environ.get('VIRTUAL_ENV', '')}/bin/python {script_path}", comment=comment)
    job.setall(schedule)

    if job.is_valid():
        cron.write()
        print(f"Cron job set: {schedule} -> {script_path}")
    else:
        print("Invalid cron job schedule.")

# Example usage:
# setup_cron_job("/home/rene/Forecast-Precision-Weather/run_hourly_analysis.py")
