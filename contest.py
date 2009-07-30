import heapq
import itertools
import sys

err = sys.stderr

def main(): #open('test.txt'),
    run_on(open('download/test.txt'),
           open('download/data.txt'),
           open('download/lang.txt'))

def run_on(testfile, datafile, langfile):
    load(datafile)
    load_lang(langfile)
    print >>err, 'Language data loaded'
    for u in gen_test_users(testfile):
        print '%s:%s' % (u, ','.join(map(str, recommendations(u))))

follows = {}                    # Repos a user follows
followers = {}                  # Users who follow a repo

def gen_test_users(testfile):
    return with_progress(map(int, testfile.read().splitlines()))

def with_progress(iterable):
    for i, x in itertools.izip(itertools.count(0), iterable):
        if i % 20 == 0: print >>err, x
        yield x

def load(datafile):
    for line in datafile.read().splitlines():
        u, r = map(int, line.split(':'))
        follows.setdefault(u, []).append(r)
        followers.setdefault(r, []).append(u)
    compute_popularity()

def recommendations(u):
    rl = recommend_by_language(u)
    recs = itertools.chain(rl, popular_repos)
    rs = dedup(follows.get(u, ()), recs)
    return by_popularity(itertools.islice(rs, 10))

def by_popularity(rs):
    return sorted(rs, reverse=True, key=popularity)

def most_popular(rs):
    return heapq.nlargest(10, rs, key=popularity)

def dedup(already, rs):
    already = set(already)
    for r in rs:
        if r not in already:
            yield r
            already.add(r)

popular_repos = []
popularity_table = {}

def compute_popularity():
    global popular_repos
    n_users = float(len(follows))
    for r in followers:
        popularity_table[r] = len(followers.get(r, ())) / n_users
    popular_repos = by_popularity(followers.keys())

def popularity(r):
    return popularity_table.get(r, 0)

repo_languages = {}            # The set of languages a repo uses
language_repos = {}            # A list of the most popular repos using a language

def load_lang(file):
    for line in file.read().splitlines():
        rstr, text = line.split(':')
        pairs = [p.split(';') for p in text.split(',')]
        r = int(rstr)
        repo_languages[r] = set(language for language, nstr in pairs)
        for language, nstr in pairs:
            language_repos.setdefault(language, []).append(r)
    for language in language_repos:
        language_repos[language] = most_popular(language_repos[language])

# Recommend the most popular repos that use languages u already watches
def recommend_by_language(u):
    languages = languages_followed_by(u)
    return most_popular(union(map(repos_using_language, languages)))

empty = frozenset()

def languages_followed_by(u):
    return union(repo_languages.get(r, empty)
                 for r in follows.get(u, ()))

def repos_using_language(language):
    return set(language_repos.get(language, ()))

def union(sets):
    return reduce(lambda s1, s2: s1 | s2, sets, set())

if __name__ == '__main__':
    main()
