import os
import re
import sys
import platform
import subprocess

from distutils.core import setup
from distutils.cmd import Command
from distutils.dist import Distribution
from distutils.command.install_data import install_data
from distutils.log import info, warn
from distutils.errors import DistutilsFileError

from tuxtremsplit.application import Application


class TxsDist(Distribution):
    global_options = Distribution.global_options + [
        ("without-icon-cache", None,
         "Don't attempt to run gtk-update-icon-cache"),
        ("without-mime-database", None,
         "Don't attempt to run update-mime-database"),
        ("without-xdg-mime-install", None,
         "Don't attempt to run xdg-mime install"),
        ("without-xdg-mime-default", None,
         "Don't attempt to run xdg-mime default"),
        ("without-desktop-database", None,
         "Don't attempt to run update-desktop-database"),
        ("without-nautilus-extension", None,
         "Don't attempt to install the nautilus extension")]

    def __init__(self, * args):
        self.without_icon_cache = False
        self.without_mime_database = False
        self.without_xdg_mime_install = False
        self.without_xdg_mime_default = False
        self.without_desktop_database = False
        self.without_nautilus_extension = False
        Distribution.__init__(self, * args)


class AdditionalCommands(object):

    def __init__(self):
        self.__distribution = None

    def get_distribution(self):
        return self.__distribution

    def set_distribution(self, distribution):
        self.__distribution = distribution
    distribution = property(get_distribution, set_distribution)

    def run(self):
        if not self.distribution.without_icon_cache:
            self._update_icon_cache()
        if not self.distribution.without_desktop_database:
            self._update_desktop_database()
        if not self.distribution.without_mime_database:
            self._update_mime_database()

    def _update_desktop_database(self):
        info("running update-desktop-database")
        try:
            subprocess.call(["update-desktop-database"])
        except Exception, e:
            warn("updating desktop database failed: %s" % str(e))

    def _update_icon_cache(self):
        info("running gtk-update-icon-cache")
        try:
            subprocess.call(["gtk-update-icon-cache", "-q", "-f", "-t",
                             "/usr/share/icons/hicolor"])
            subprocess.call(["gtk-update-icon-cache", "-q", "-f", "-t",
                             "/usr/local/share/icons/hicolor"])

            for folder in os.listdir("/home"):
                hicolor_path = "/home/%s/.local/share/icons/hicolor" % folder
                if os.path.exists(hicolor_path):
                    info("running gtk-update-icon-cache for /home/" + folder)
                    subprocess.call(["gtk-update-icon-cache", "-q", "-f",
                                     "-t", hicolor_path])

        except Exception, e:
            warn("updating the GTK icon cache failed: %s" % str(e))

    def _update_mime_database(self):
        info("running update-mime-database")
        try:
            subprocess.call(["update-mime-database", "/usr/share/mime"])
            subprocess.call(["update-mime-database", "/usr/local/share/mime"])
        except Exception, e:
            warn("updating mime database failed: %s" % str(e))


class InstallData(install_data):

    def run(self):
        install_data.run(self)
        if not self.distribution.without_xdg_mime_install:
            self._xdg_mime_install()
        if not self.distribution.without_xdg_mime_default:
            self._xdg_mime_default()

        addcmds = AdditionalCommands()
        addcmds.distribution = self.distribution
        addcmds.run()

        source = os.path.join(self.install_dir, "bin/txs")
        dest = os.path.join(self.install_dir, "bin/tuxtremsplit")
        info("creating symbolic link of %s to %s" % (source,
                                                     dest))
        create_symlink = True

        if re.match(".*tuxtremsplit-[\d.]*\d+.*/debian/.*", self.install_dir):
            warn("As you're not installing tuxtremsplit in standard path "
                 "(like /usr for example), I don't create the symbolic link.")
            create_symlink = False

        if os.path.exists(dest):
            warn("The file %s already exists. Nothing to do." % dest)
            create_symlink = False

        if create_symlink:
            try:
                subprocess.call(["ln", "-s", source, dest])
            except Exception, e:
                warn("Executable link creation failed: %s" % str(e))

    def _xdg_mime_install(self):
        info("running xdg-mime install %s" %
             os.path.join(self.install_dir,
             "share/mime/packages/xtm-mimetype.xml"))
        try:
            subprocess.call(["xdg-mime", "install", os.path.join(
                            self.install_dir,
                            "share/mime/packages/xtm-mimetype.xml")])
        except Exception, e:
            warn("xdg-mime install failed: %s" % str(e))

    def _xdg_mime_default(self):
        info("running xdg-mime default tuxtremsplit.desktop "
             "application/x-extension-xtm")
        try:
            subprocess.call(["xdg-mime", "default", "tuxtremsplit.desktop",
                             "application/x-extension-xtm"])
        except Exception, e:
            warn("xdg-mime default failed: %s" % str(e))


class Uninstall(Command):
    description = "Attempt an uninstall from an install --record file"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def get_command_name(self):
        return 'uninstall'

    def run(self):
        try:
            f = open("uninstall.list")
            files = [file.strip() for file in f]
            f.close()
        except:
            raise DistutilsFileError("Unable to open uninstall.list. "
                                     "Did you try an uninstall without "
                                     "install before ?\nPlease do a 'python "
                                     "setup.py install' and then restart me.")

        for file in files:
            if os.path.isfile(file) or os.path.islink(file):
                info("removing %s" % repr(file))
                if not self.dry_run:
                    try:
                        os.unlink(file)
                    except OSError, e:
                        warn("could not delete: %s: %s" % (repr(file), e))
            elif not os.path.isdir(file):
                info("skipping %s" % repr(file))

        dirs = set()
        for file in reversed(sorted(files)):
            dir = os.path.dirname(file)
            if dir not in dirs and os.path.isdir(dir) and \
               len(os.listdir(dir)) == 0:
                dirs.add(dir)
                # Only nuke empty Python library directories, else we could
                # destroy
                # e.g. locale directories we're the only app
                # with a .mo installed for.
                if dir.find("site-packages/") > 0:
                    info("removing %s" % repr(dir))
                    if not self.dry_run:
                        try:
                            os.rmdir(dir)
                        except OSError, e:
                            warn("could not remove directory: %s" % str(e))
                else:
                    info("skipping empty directory %s" % repr(dir))

        addcmds = AdditionalCommands()
        addcmds.distribution = self.distribution
        addcmds.run()


if sys.argv[1] == "install" and not "--record" in sys.argv:
    sys.argv.append("--record")
    sys.argv.append("uninstall.list")

man_dir = 'man' if platform.system() == 'FreeBSD' else 'share/man'

data_files = [
        ('share/tuxtremsplit/config/', ['config/settings.yml']),
        ('share/tuxtremsplit/pixmaps/', ['pixmaps/tuxtremsplit.png',
         'pixmaps/small_tuxtremsplit.png',
         'pixmaps/xtm_content.png', 'pixmaps/mini-cube.png',
         'pixmaps/xtm-mime.png']),
        ('share/tuxtremsplit/glade/', ['glade/actionwindow.glade',
                                       'glade/mainwindow.glade']),
        ('share/mime/packages/', ['mime_type/xtm-mimetype.xml']),
        ('share/applications/', ['tuxtremsplit.desktop']),
        ('/usr/share/icons/hicolor/16x16/apps/',
         ['pixmaps/icons/16x16/tuxtremsplit.png']),
        ('/usr/share/icons/hicolor/22x22/apps/',
         ['pixmaps/icons/22x22/tuxtremsplit.png']),
        ('/usr/share/icons/hicolor/24x24/apps/',
         ['pixmaps/icons/24x24/tuxtremsplit.png']),
        ('/usr/share/icons/hicolor/32x32/apps/',
         ['pixmaps/icons/32x32/tuxtremsplit.png']),
        ('/usr/share/icons/hicolor/48x48/apps/',
         ['pixmaps/icons/48x48/tuxtremsplit.png']),
        ('/usr/share/icons/hicolor/64x64/apps/',
         ['pixmaps/icons/64x64/tuxtremsplit.png']),
        ('/usr/share/icons/hicolor/128x128/apps/',
         ['pixmaps/icons/128x128/tuxtremsplit.png']),
        ('/usr/share/icons/hicolor/256x256/apps/',
         ['pixmaps/icons/256x256/tuxtremsplit.png']),
        ('/usr/share/icons/hicolor/16x16/mimetypes/',
         ['pixmaps/mime/16x16/application-x-extension-xtm.png']),
        ('/usr/share/icons/hicolor/22x22/mimetypes/',
         ['pixmaps/mime/22x22/application-x-extension-xtm.png']),
        ('/usr/share/icons/hicolor/24x24/mimetypes/',
         ['pixmaps/mime/24x24/application-x-extension-xtm.png']),
        ('/usr/share/icons/hicolor/32x32/mimetypes/',
         ['pixmaps/mime/32x32/application-x-extension-xtm.png']),
        ('/usr/share/icons/hicolor/36x36/mimetypes/',
         ['pixmaps/mime/36x36/application-x-extension-xtm.png']),
        ('/usr/share/icons/hicolor/48x48/mimetypes/',
         ['pixmaps/mime/48x48/application-x-extension-xtm.png']),
        ('/usr/share/icons/hicolor/64x64/mimetypes/',
         ['pixmaps/mime/64x64/application-x-extension-xtm.png']),
        ('/usr/share/icons/hicolor/128x128/mimetypes/',
         ['pixmaps/mime/128x128/application-x-extension-xtm.png']),
        ('/usr/share/icons/hicolor/192x192/mimetypes/',
         ['pixmaps/mime/192x192/application-x-extension-xtm.png']),
        ('/usr/share/icons/hicolor/256x256/mimetypes/',
         ['pixmaps/mime/256x256/application-x-extension-xtm.png']),
        (os.path.join(man_dir, 'fr/man8'), ['man/fr/tuxtremsplit.8']),
        (os.path.join(man_dir, 'man8'), ['man/fr/tuxtremsplit.8'])]

if not "--without-nautilus-extension" in sys.argv:
    data_files.append(('/usr/lib/nautilus/extensions-2.0/python/',
                       ["nautilus_extension/nautilus-tuxtremsplit.py"]))

setup(name=Application().settings.name,
      version=Application().settings.version,
      packages=['tuxtremsplit',
                'tuxtremsplit.application',
                'tuxtremsplit.core',
                'tuxtremsplit.gtk2'],
      scripts=['txs'],
      data_files=data_files,
      author=Application().settings.author,
      author_email=Application().settings.author_email,
      url=Application().settings.homepage,
      keywords=['xtremsplit', 'xtm'],
      license='GNU GPLv3',
      description=Application().settings.description,
      cmdclass={'install_data': InstallData, 'uninstall': Uninstall},
      distclass=TxsDist)
