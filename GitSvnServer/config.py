
import re
import sys

repos_re = re.compile(r'^\[repos "(?P<url_base>.*)"\]\s*$')
var_re = re.compile(r'^\s+(?P<name>\S+)\s*=\s*((?P<value>\S+)|"(?P<qvalue>.*)")\s*$')

class ConfigError(Exception):
    pass

class Repos:
    location = ''
    kind = 'git'

    def __str__(self):
        s = ""
        for a in [x for x in Repos.__dict__ if not x.startswith('_')]:
            s += "  %s: %s\n" % (a, self.__dict__[a])
        return s

class Config:
    def __init__(self, name=None):
        self.repos = {}
        self.filename = name

    def load(self, filename=None):
        if filename is not None:
            self.filename = filename
        try:
            self.__parse()
        except Exception, e:
            print >> sys.stderr, "Failed to load configuration from '%s':\n%s" \
                  % (self.filename, str(e))
            sys.exit(1)

    def __parse(self):
        repos = None

        if self.filename is None:
            return

        f = open(self.filename)
        for i, line in enumerate(f):
            line_no = i + 1
            repos_m = repos_re.match(line)
            var_m = var_re.match(line)
            if repos_m is not None:
                url_base = repos_m.group('url_base')
                while url_base[0] == '/':
                    url_base = url_base[1:]
                while url_base[-1] == '/':
                    url_base = url_base[:-2]
                if url_base in self.repos:
                    raise ConfigError('Duplicate repos specification', line_no)
                repos = Repos()
                self.repos[url_base] = repos
            elif var_m is not None and repos is not None:
                name = var_m.group('name').lower()
                value = var_m.group('qvalue')
                if value is None:
                    value = var_m.group('value')
                if name in [x for x in Repos.__dict__ if not x.startswith('_')]:
                    repos.__dict__.setdefault(name, value)

        f.close()

    def __str__(self):
        s = ""
        for name, repos in self.repos.items():
            s += "%s\n%s" % (name, repos)
        return s

config = Config('/etc/git-svnserver/config')
