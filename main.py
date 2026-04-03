import os
import subprocess
import random
from datetime import datetime, timedelta

# ------------------ CONFIG ------------------
MAX_COMMITS_PER_DAY = 5   # control density
DAYS_BACK = 365
COMMIT_MESSAGE = "update"
# --------------------------------------------

def run_git_command(cmd, cwd, env=None):
    result = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Git command failed: {' '.join(cmd)}\n{result.stderr}")
    return result

def is_git_repo(path):
    return os.path.isdir(os.path.join(path, ".git"))

def generate_commit_schedule(total_commits):
    """Distribute commits across days instead of random clustering"""
    today = datetime.now()
    start = today - timedelta(days=DAYS_BACK)

    schedule = {}

    for _ in range(total_commits):
        day_offset = random.randint(0, DAYS_BACK - 1)
        day = (start + timedelta(days=day_offset)).date()

        if day not in schedule:
            schedule[day] = 0

        if schedule[day] < MAX_COMMITS_PER_DAY:
            schedule[day] += 1

    return schedule

def make_commit(repo_path, filename, commit_time):
    filepath = os.path.join(repo_path, filename)

    with open(filepath, "a") as f:
        f.write(f"{commit_time.isoformat()}\n")

    run_git_command(["git", "add", filename], repo_path)

    env = os.environ.copy()
    date_str = commit_time.strftime("%Y-%m-%dT%H:%M:%S")

    env["GIT_AUTHOR_DATE"] = date_str
    env["GIT_COMMITTER_DATE"] = date_str

    run_git_command(["git", "commit", "-m", COMMIT_MESSAGE], repo_path, env)

def main():
    repo_path = input("Repo path (default .): ").strip() or "."
    filename = input("Filename (default data.txt): ").strip() or "data.txt"
    total_commits = int(input("Total commits: ").strip() or 50)

    if not is_git_repo(repo_path):
        print("❌ Not a git repository")
        return

    schedule = generate_commit_schedule(total_commits)

    print(f"\n📅 Commit distribution over {len(schedule)} days\n")

    for day, count in sorted(schedule.items()):
        for _ in range(count):
            seconds = random.randint(0, 86399)
            commit_time = datetime.combine(day, datetime.min.time()) + timedelta(seconds=seconds)

            print(f"Committing on {commit_time}")
            make_commit(repo_path, filename, commit_time)

    print("\n🚀 Pushing...")
    run_git_command(["git", "push"], repo_path)

    print("✅ Done")

if __name__ == "__main__":
    main()