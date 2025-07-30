from enum import Enum


class DataType(str, Enum):
    PDF = "pdf"
    CSV = "csv"
    JSON = "json"
    TXT = "txt"
    XML = "xml"
    DOCX = "docx"
    MDX = "mdx"

    # Database types
    MYSQL = "mysql"
    POSTGRES = "postgres"

    # Repository types
    GITHUB = "github"
    DIRECTORY = "directory"

    # Web types
    WEBSITE = "website"
    YOUTUBE = "youtube"

    # Raw types
    TEXT = "text"
    RAW = "raw"
