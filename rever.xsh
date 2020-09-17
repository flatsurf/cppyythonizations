######################################################################
#  This file is part of cppyythonizations.
#
#        Copyright (C) 2020 Julian Rüth
#
#  cppyythonizations is free software: you can redistribute it and/or modify it
#  under the terms of the GNU Lesser General Public License as published by the
#  Free Software Foundation, either version 3 of the License, or (at your
#  option) any later version.
#
#  cppyythonizations is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
#  or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#
#  You should have received a copy of the GNU General Public License along with
#  cppyythonizations. If not, see <https://www.gnu.org/licenses/>.
#####################################################################

import sys

try:
  input("Are you sure you are on the master branch which is identical to origin/master? [ENTER]")
except KeyboardInterrupt:
  sys.exit(1)

sys.path.insert(0, 'recipe/snippets/rever')

import dist

$PROJECT = 'cppyythonizations'

$ACTIVITIES = [
    'version_bump',
    'changelog',
    'dist',
    'tag',
    'push_tag',
    'ghrelease',
]

$VERSION_BUMP_PATTERNS = [
    ('configure.ac', r'AC_INIT', r'AC_INIT([cppyythonizations], [$VERSION], [julian.rueth@fsfe.org])'),
    ('recipe/meta.yaml', r"\{% set version =", r"{% set version = '$VERSION' %}"),
    ('recipe/meta.yaml', r"\{% set build_number =", r"{% set build_number = '0' %&"),
]

$CHANGELOG_FILENAME = 'ChangeLog'
$CHANGELOG_TEMPLATE = 'TEMPLATE.rst'
$PUSH_TAG_REMOTE = 'git@github.com:flatsurf/cppyythonizations.git'

$GITHUB_ORG = 'flatsurf'
$GITHUB_REPO = 'cppyythonizations'

$GHRELEASE_ASSETS = ['cppyythonizations-' + $VERSION + '.tar.gz']
