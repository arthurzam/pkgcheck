# Copyright: 2006 Brian Harring <ferringb@gmail.com>
# License: GPL2


from pkgcore_checks.base import Template, package_feed, Result


class DroppedKeywordsReport(Template):
    """scan pkgs for keyword dropping across versions"""

    feed_type = package_feed

    def __init__(self, options):
        Template.__init__(self, options)
        self.arches = dict((k, None) for k in options.arches)

    def feed(self, pkgsets, reporter):
        for pkgset in pkgsets:
            yield pkgset
            if len(pkgset) == 1:
                continue

            lastpkg = pkgset[-1]
            state = set(x.lstrip("~") for x in lastpkg.keywords)
            arches = set(self.arches)
            dropped = []
            for pkg in reversed(pkgset[:-1]):
                oldstate = set(x.lstrip("~") for x in pkg.keywords)
                for key in oldstate.difference(state):
                    if key.startswith("-"):
                        continue
                    elif "-%s" % key in state:
                        continue
                    elif key in arches:
                        dropped.append((key, lastpkg))
                        arches.discard(key)
                state = oldstate
                lastpkg = pkg
            for key, pkg in dropped:
                reporter.add_report(DroppedKeywordWarning(key, pkg))


class DroppedKeywordWarning(Result):
    """Arch keywords dropped during pkg version bumping"""

    __slots__ = ("arch", "category", "package", "version")

    def __init__(self, arch, pkg):
        Result.__init__(self)
        self._store_cpv(pkg)
        self.arch = arch

    def to_str(self):
        return "%s/%s-%s: dropped keyword %s" % (self.category, self.package,
            self.version, self.arch)

    def to_xml(self):
        return \
"""<check name="%s">
    <category>%s</category>
    <package>%s</package>
    <version>%s</version>
    <arch>%s</arch>
    <msg>keyword was dropped</msg>
</check>""" % (self.__class__.__name__, self.category, self.package,
    self.version, self.arch)
