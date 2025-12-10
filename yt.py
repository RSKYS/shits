import os
import sys
import subprocess
import json
from pathlib import Path
from tqdm import tqdm

DOWNLOAD_FOLDER = "/var/lib/red-ext"
BROWSER = "firefox"
COOKIES_FILE = "cookies.txt"
JS_RUNTIME = "deno"
ENABLE_REMOTE_EJS = True


def is_playlist(url: str) -> bool:
	return "list=" in url or "playlist" in url

def get_playlist_info(url: str) -> tuple[int, str]:
	cmd = ["yt-dlp", "--dump-json", "--flat-playlist", url]
	try:
		result = subprocess.run(cmd, capture_output=True, text=True, check=True)
		entries = [json.loads(line) for line in result.stdout.strip().splitlines() if line.strip()]
		total = len(entries)
		title = entries[0].get("playlist_title") or entries[0].get("title", "Unknown")
		return total, title
	except:
		return 1, "Unknown"

def download_with_perfect_progress(url: str):
	Path(DOWNLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

	total, title = get_playlist_info(url)
	is_pl = is_playlist(url)

	print(f"{'Playlist' if is_pl else 'Video'}: {title}")
	print(f"Total items: {total}")
	print(f"Saving to: {DOWNLOAD_FOLDER}")
	print("-" * 70)

	cmd = [
		"yt-dlp",
		"--print-json",
		"--newline",
		"--ignore-errors",
		"--retries", "infinite",
		"--sleep-interval", "3",
		"--max-sleep-interval", "10",
		"--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
		"--restrict-filenames",
		"--progress-template", 'download:{"status":"%(progress.status)s", "filename":"%(progress.filename)s", "percent":"%(progress._percent_str)s", "speed":"%(progress._speed_str)s", "eta":"%(progress._eta_str)s"}',
	]


	if JS_RUNTIME:
		cmd += ["--js-runtimes", JS_RUNTIME]
	if ENABLE_REMOTE_EJS:
		cmd += ["--remote-components", "ejs:github"]

	if os.path.exists(COOKIES_FILE):
		cmd += ["--cookies", COOKIES_FILE]
	else:
		cmd += ["--cookies-from-browser", BROWSER]

	if PREFER_MP4 := True:
		cmd += ["-f", "best[ext=mp4]/bestvideo[ext=mp4]+bestaudio/best"]

	if is_pl:
		cmd += ["-o", f"{DOWNLOAD_FOLDER}/%(playlist_index)03d - %(title)s.%(ext)s"]
	else:
		cmd += ["-o", f"{DOWNLOAD_FOLDER}/%(title)s.%(ext)s"]

	cmd += [url]

	proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

	downloaded = 0
	pbar = tqdm(total=total, unit="video", desc="Starting...", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}")

	current_file = ""

	for line in proc.stdout:
		line = line.strip()
		if not line:
			continue

		try:
			data = json.loads(line)

			# File started
			if data.get("status") == "downloading" and data.get("filename"):
				current_file = os.path.basename(data["filename"])
				speed = data.get("_speed_str", "?")
				percent = data.get("_percent_str", "0%")
				eta = data.get("_eta_str", "?")
				pbar.set_description(f"{current_file[:50]} → {percent} @ {speed} | ETA {eta}")

			# File finished
			if data.get("status") == "finished":
				downloaded += 1
				pbar.update(1)
				pbar.set_description(f"Finished: {current_file[:60]}")

		except json.JSONDecodeError:
			if "has already been downloaded" in line:
				downloaded += 1
				pbar.update(1)
				pbar.set_description("Skipped (exists)")
			elif "ERROR" in line.upper():
				print(f"ERROR: {line}")

	proc.wait()
	pbar.close()
	print(f"\nDone! Processed {downloaded}/{total} items successfully.")

def main():
	if len(sys.argv) != 2:
		print("Usage: python dl.py <YouTube URL>")
		sys.exit(1)

	url = sys.argv[1].strip()
	if not url.startswith("http"):
		print("Invalid URL")
		sys.exit(1)

	try:
		download_with_perfect_progress(url)
	except KeyboardInterrupt:
		print("\nCancelled by user")
	except Exception as e:
		print(f"Error: {e}")

if __name__ == "__main__":
	main()

