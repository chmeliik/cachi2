import abc
from pathlib import Path
from typing import Callable, Generic, TypeVar

from cachi2.core.checksum import ChecksumInfo
from cachi2.core.models.output import Dependency

DependencyT_contra = TypeVar("DependencyT_contra", contravariant=True)


class DependencyStorage(abc.ABC, Generic[DependencyT_contra]):
    """Permanent storage for a certain type (or types) of dependency.

    >>> class PipStorage(DependencyStorage[PipDependency]):
            '''Permanent storage for pip dependencies.'''

    >>> class GenericStorage(DependencyStorage[PipDependency | NpmDependency]):
            '''Permanent storage for pip or npm dependencies.'''

    Because the type param is contravariant, you can do things like this:

    >>> generic_storage = GenericStorage()
    >>> pip_storage: DependencyStorage[PipDependency] = generic_storage

    I.e. a more generic implementation satisfies the type constraints of a more specific use case.
    """

    @abc.abstractmethod
    def retrieve_dependency(
        self,
        dependency: DependencyT_contra,
        checksums: list[ChecksumInfo],
        consume: Callable[[Path], None],
    ) -> bool:
        """If the dependency archive is present in permanent storage, retrieve it.

        :param dependency: metadata about the dependency to retrieve
        :param checksums: the checksum of the dependency archive must match a checksum in this list
                          (unless the list is empty)
        :param consume: process the the dependency archive
        :return: True if the dependency was retrieved, False otherwise
        """
        return False

    @abc.abstractmethod
    def store_dependency(
        self, dependency: DependencyT_contra, checksums: list[ChecksumInfo], dep_archive: Path
    ) -> None:
        """Store the downloaded dependency archive in permanent storage.

        :param dependency: metadata about the dependency to store
        :param checksums: TBD how do you explain why they're needed here
        :param dep_archive: path to the downloaded dependency archive
        """
        pass


class NoStorage(DependencyStorage[Dependency]):
    def retrieve_dependency(
        self,
        dependency: Dependency,
        checksums: list[ChecksumInfo],
        consume: Callable[[Path], None],
    ) -> bool:
        return False

    def store_dependency(
        self, dependency: Dependency, checksums: list[ChecksumInfo], dep_archive: Path
    ) -> None:
        pass


# class DependencyDownloader(abc.ABC, Generic[DependencyT_contra]):
#     """Downloader for a certain type (or types) of dependencies."""

#     permanent_storage: Optional[DependencyStorage[DependencyT_contra]]

#     @abc.abstractmethod
#     def download_from_upstream(
#         self, dependency: DependencyT_contra, checksums: list[ChecksumInfo], path: Path
#     ) -> None:
#         pass

#     def download(
#         self, dependency: DependencyT_contra, checksums: list[ChecksumInfo], path: Path
#     ) -> None:
#         if not self.permanent_storage:
#             self.download_from_upstream(dependency, checksums, path)
#             return

#         if not self.permanent_storage.retrieve_dependency(dependency, checksums, path):
#             self.download_from_upstream(dependency, checksums, path)
#             self.permanent_storage.store_dependency(dependency, checksums, path)
