DEFAULT_COMMAND_MAP = {
    ".c": "$CC -o $target $CFLAGS $CCFLAGS $sources",
    ".cpp": "$CXX -o $target $CXXFLAGS $CCFLAGS $sources",
}
