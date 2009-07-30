import heapq
import itertools
import sys

err = sys.stderr

def main():
    run_on(open('download/data.txt'),
           open('download/test.txt'))

def run_on(datafile, testfile):
    load(datafile)
    print >>err, 'Loaded'
    for u in gen_test_users(testfile):
        print '%s:%s' % (u, ','.join(map(str, recommendations(u))))

follows = {}                    # Repos a user follows
followers = {}                  # Users who follow a repo

def gen_test_users(testfile):
    return with_progress(map(int, testfile.read().splitlines()))

def with_progress(iterable):
    for i, x in itertools.izip(itertools.count(0), iterable):
        if i % 100 == 0: print >>err, x
        yield x

def load(datafile):
    for line in datafile.read().splitlines():
        u, r = map(int, line.split(':'))
        follows.setdefault(u, []).append(r)
        followers.setdefault(r, []).append(u)
    print >>err, 'Data read'
    compute_popularity()

def recommendations(u):
    return itertools.islice((r for r in popular_repos if r not in follows.get(u, ())),
                            10)

popular_repos = []
popularity_table = {}

def compute_popularity():
    global popular_repos
    popular_repos = followers.keys()
    n_users = float(len(follows))
    for r in popular_repos:
        popularity_table[r] = len(followers.get(r, ())) / n_users
    popular_repos.sort(reverse=True, key=popularity)

def popularity(r):
    return popularity_table[r]

if __name__ == '__main__':
    main()
