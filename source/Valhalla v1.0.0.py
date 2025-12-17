# valhalla.py — The Password Cracker of the Gods (FINAL ETERNAL 2024 EDITION)
# Full CPU · Resume Forever · MD5/SHA256 Auto-Detect · Unstoppable · Pure Python

import argparse
import itertools
import hashlib
import multiprocessing as mp
import string
import time
import os
import sys

VALHALLA_BANNER = """
██╗   ██╗ █████╗ ██╗     ██╗  ██╗ █████╗ ██╗     ██╗      █████╗
██║   ██║██╔══██╗██║     ██║  ██║██╔══██╗██║     ██║     ██╔══██╗
██║   ██║███████║██║     ███████║███████║██║     ██║     ███████║
╚██╗ ██╔╝██╔══██║██║     ██╔══██║██╔══██║██║     ██║     ██╔══██║
 ╚████╔╝ ██║  ██║███████╗██║  ██║██║  ██║███████╗███████╗██║  ██║
  ╚═══╝  ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝

                 WHERE PASSWORDS GO TO DIE 
"""

CHARSETS = {
    "digits": string.digits,
    "lower": string.ascii_lowercase,
    "upper": string.ascii_uppercase,
    "letters": string.ascii_letters,
    "alnum": string.ascii_letters + string.digits,
    "all": string.ascii_letters + string.digits + string.punctuation,
}
RESUME_FILE = ".valhalla_resume"
SAVE_INTERVAL = 10000


def detect_hash_type(h):
    h = h.strip().lower()
    if len(h) == 32 and all(c in "0123456789abcdef" for c in h):
        return "md5"
    if len(h) == 64 and all(c in "0123456789abcdef" for c in h):
        return "sha256"
    raise ValueError("Only MD5 & SHA256 supported")


def compute_hash(text, algo):
    if algo == "md5":
        return hashlib.md5(text.encode()).hexdigest()
    return hashlib.sha256(text.encode()).hexdigest()


def load_resume():
    if os.path.exists(RESUME_FILE):
        try:
            return int(open(RESUME_FILE).read().strip())
        except:
            return 0
    return 0


def save_resume(val):
    with open(RESUME_FILE, "w") as f:
        f.write(str(val))


def clear_resume():
    if os.path.exists(RESUME_FILE):
        os.remove(RESUME_FILE)


def is_match(guess, target, mode, algo=None):
    if mode == "normal":
        return guess == target
    return compute_hash(guess, algo) == target.lower()


def worker(pid, n_procs, args, counter, found, start_from):
    charset = args.charset
    for length in range(args.min_len, args.max_len + 1):
        if found.value:
            return
        for combo in itertools.product(charset, repeat=length):
            if found.value:
                return
            idx = counter.value
            counter.value += 1
            if idx < start_from or idx % n_procs != pid:
                continue
            guess = "".join(combo)
            if is_match(guess, args.target, args.mode, args.algo):
                found.value = 1
                print(f"\n\n[+] VALHALLA HAS SPOKEN → {guess}")
                clear_resume()
                return
            if counter.value % SAVE_INTERVAL == 0:
                save_resume(counter.value)
                print(f"\rAttempts: {counter.value:,} | Trying: {guess}", end="", flush=True)


def brute_force(args):
    resume_from = load_resume() if args.resume else 0
    print(f"[+] Target     : {args.target}")
    print(f"[+] Length     : {args.min_len} → {args.max_len}")
    print(f"[+] Charset    : {len(args.charset)} characters")
    print(f"[+] Warriors   : {mp.cpu_count()} cores")
    if resume_from:
        print(f"[+] Resuming from attempt #{resume_from:,}")

    manager = mp.Manager()
    counter = manager.Value("i", resume_from)
    found = manager.Value("i", 0)

    processes = []
    start_time = time.time()

    for pid in range(mp.cpu_count()):
        p = mp.Process(target=worker, args=(pid, mp.cpu_count(), args, counter, found, resume_from))
        p.start()
        processes.append(p)

    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        save_resume(counter.value)
        print(f"\n[!] Odin calls you back — progress saved in Valhalla")
        return

    elapsed = time.time() - start_time
    if not found.value:
        print(f"\n[-] Not even Valhalla could break this one ({elapsed:.2f}s)")


def wordlist_mode(args):
    if not os.path.exists(args.wordlist):
        print(f"[-] Wordlist lost in the void: {args.wordlist}")
        return

    print(f"[+] Summoning ancient scrolls → {args.wordlist}")
    tried = 0
    start_time = time.time()

    with open(args.wordlist, "r", errors="ignore") as f:
        for line in f:
            word = line.strip()
            if not word:
                continue
            tried += 1
            if is_match(word, args.target, args.mode, args.algo):
                elapsed = time.time() - start_time
                print(f"\n\n[+] THE GODS HAVE CHOSEN → {word}")
                print(f"[+] Cracked in {tried:,} attempts ({elapsed:.2f}s)")
                return
            if tried % 1000 == 0:
                print(f"\rTried {tried:,} souls...", end="", flush=True)

    print(f"\n[-] This soul resists even Valhalla")


def main():
    print(VALHALLA_BANNER)

    if len(sys.argv) == 1:
        print("Mortal, you dare summon Valhalla without offering a soul?\n")
        print("Choose your weapon:")
        print("  brute     → Unleash infinite brute force")
        print("  wordlist  → Summon ancient forbidden scrolls\n")
        print("Examples:")
        print("  python valhalla.py brute abc123 --max 10")
        print("  python valhalla.py brute 5d41402abc4b2a76b9719d911017c592 --max 8")
        print("  python valhalla.py wordlist <hash> -w rockyou.txt")
        print("  python valhalla.py brute <hash> --resume")
        print("\nRun 'python valhalla.py <mode> --help' for full glory")
        sys.exit(0)

    parser = argparse.ArgumentParser(description="VALHALLA — The Password Cracker of the Gods")
    sub = parser.add_subparsers(dest="mode", required=True)

    brute = sub.add_parser("brute", help="Brute force the heavens")
    brute.add_argument("target", help="Password or hash to destroy")
    brute.add_argument("--min", type=int, default=1, dest="min_len", help="Minimum length")
    brute.add_argument("--max", type=int, default=8, dest="max_len", help="Maximum length")
    brute.add_argument("--charset", choices=CHARSETS.keys(), default="alnum", help="Character set")
    brute.add_argument("--resume", action="store_true", help="Resume from last battle")

    wl = sub.add_parser("wordlist", help="Summon ancient knowledge")
    wl.add_argument("target", help="Password or hash to destroy")
    wl.add_argument("-w", "--wordlist", required=True, help="Path to scroll of passwords")

    args = parser.parse_args()

    if args.mode == "brute":
        args.charset = CHARSETS[args.charset]
        try:
            args.algo = detect_hash_type(args.target)
            args.mode = "hash"
            print(f"[+] Detected {args.algo.upper()} hash — worthy opponent")
        except:
            args.algo = None
            args.mode = "normal"
        brute_force(args)

    elif args.mode == "wordlist":
        try:
            args.algo = detect_hash_type(args.target)
            args.mode = "hash"
        except:
            args.algo = None
            args.mode = "normal"
        wordlist_mode(args)


if __name__ == "__main__":
    mp.set_start_method("spawn", force=True)
    main()