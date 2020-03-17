import sys
from threading import Lock
from typing import Optional, List, Pattern, TextIO, Tuple

from modules.datafile import rom
from modules.utils import check_in_pattern_list


class FileData:
    def __init__(self, size: int, path: str):
        self.size = size
        self.path = path


class FileDataUtils:
    @staticmethod
    def get_size(file_data: FileData) -> int:
        return file_data.size


class Score:
    def __init__(
            self,
            region: int,
            languages: int,
            revision: List[int],
            version: List[int],
            sample: List[int],
            demo: List[int],
            beta: List[int],
            proto: List[int]):
        self.region = region
        self.languages = languages
        self.revision = revision
        self.version = version
        self.sample = sample
        self.demo = demo
        self.beta = beta
        self.proto = proto

    def __repr__(self) -> str:
        return str(self.__dict__)


class GameEntry:
    def __init__(
            self,
            is_bad: bool,
            is_prerelease: bool,
            region: str,
            languages: List[str],
            input_index: int,
            revision: str,
            version: str,
            sample: str,
            demo: str,
            beta: str,
            proto: str,
            is_parent: bool,
            name: str,
            roms: List[rom]):
        self.is_bad = is_bad
        self.is_prerelease = is_prerelease
        self.region = region
        self.languages = languages
        self.input_index = input_index
        self.revision = revision
        self.version = version
        self.sample = sample
        self.demo = demo
        self.beta = beta
        self.proto = proto
        self.is_parent = is_parent
        self.name = name
        self.roms = roms
        self.score: Optional[Score] = None

    def __repr__(self) -> str:
        return str(self.__dict__)


class GameEntryHelper:

    @staticmethod
    def get_revision(g: GameEntry) -> str:
        return g.revision

    @staticmethod
    def get_version(g: GameEntry) -> str:
        return g.version

    @staticmethod
    def get_sample(g: GameEntry) -> str:
        return g.sample

    @staticmethod
    def get_demo(g: GameEntry) -> str:
        return g.demo

    @staticmethod
    def get_beta(g: GameEntry) -> str:
        return g.beta

    @staticmethod
    def get_proto(g: GameEntry) -> str:
        return g.proto

    @staticmethod
    def set_revision(g: GameEntry, revision: str) -> None:
        g.revision = revision

    @staticmethod
    def set_version(g: GameEntry, version: str) -> None:
        g.version = version

    @staticmethod
    def set_sample(g: GameEntry, sample: str) -> None:
        g.sample = sample

    @staticmethod
    def set_demo(g: GameEntry, demo: str) -> None:
        g.demo = demo

    @staticmethod
    def set_beta(g: GameEntry, beta: str) -> None:
        g.beta = beta

    @staticmethod
    def set_proto(g: GameEntry, proto: str) -> None:
        g.proto = proto


class GameEntryKeyGenerator:
    def __init__(
            self,
            prioritize_languages: bool,
            prefer_prereleases: bool,
            prefer_parents: bool,
            input_order: bool,
            prefer: List[Pattern],
            avoid: List[Pattern]):
        self.prioritize_languages = prioritize_languages
        self.prefer_prereleases = prefer_prereleases
        self.prefer_parents = prefer_parents
        self.input_order = input_order
        self.avoid = avoid
        self.prefer = prefer

    def generate(self, g: GameEntry) -> Tuple:
        return (
            g.is_bad,
            self.prefer_prereleases ^ g.is_prerelease,
            check_in_pattern_list(g.name, self.avoid),
            g.score.languages if self.prioritize_languages else g.score.region,
            g.score.region if self.prioritize_languages else g.score.languages,
            self.prefer_parents and not g.is_parent,
            g.input_index if self.input_order else 0,
            not check_in_pattern_list(g.name, self.prefer),
            g.score.revision,
            g.score.version,
            g.score.sample,
            g.score.demo,
            g.score.beta,
            g.score.proto,
            -len(g.languages),
            not g.is_parent)


class RegionData:
    def __init__(
            self,
            code: str,
            pattern: Optional[Pattern[str]],
            languages: List[str]):
        self.code = code
        self.pattern = pattern
        self.languages = languages


class ProgressBar:
    def __init__(
            self,
            count: int,
            prefix: str = '',
            size: int = 60):
        self.count = count
        self.prefix = prefix
        self.size = size
        self.curr = 0
        self.lock = Lock()

    def print(
            self,
            increase: int = 1,
            output_file: TextIO = sys.stderr) -> None:
        with self.lock:
            self.curr += increase
            x = int(self.size * self.curr / self.count)
            print(
                '%s [%s%s] %i/%i\033[K' % (
                    self.prefix,
                    '#' * x,
                    '.' * (self.size - x),
                    self.curr,
                    self.count),
                end='\n' if self.curr == self.count else '\r',
                file=output_file)
