GNU_INSTALL_ROOT := /usr

ADD_FEATURE_VECTOR?=y
ADD_SEGMENT_DATA?=n
ADD_SEGMENT_DATA?=n

SML_FLAGS += -DKB_USE_SW_PME

ifeq ($(ADD_FEATURE_VECTOR), y)
SML_FLAGS += -DSML_ADD_FEATURE_VECTOR=1
else
SML_FLAGS += -DSML_ADD_FEATURE_VECTOR=0
endif

ifeq ($(ADD_SEGMENT_DATA), y)
SML_FLAGS += -DSML_ADD_SEGMENT_DATA=1
else
SML_FLAGS += -DSML_ADD_SEGMENT_DATA=0
endif

# Toolchain commands
CC              := '$(GNU_INSTALL_ROOT)/bin/x86_64-w64-mingw32-gcc'
CXX              := '$(GNU_INSTALL_ROOT)/bin/x86_64-w64-mingw32-g++'
AS              := '$(GNU_INSTALL_ROOT)/bin/x86_64-w64-mingw32-as'
AR              := '$(GNU_INSTALL_ROOT)/bin/x86_64-w64-mingw32-ar' -r
LD              := '$(GNU_INSTALL_ROOT)/bin/x86_64-w64-mingw32-ld'
NM              := '$(GNU_INSTALL_ROOT)/bin/x86_64-w64-mingw32-nm'
OBJDUMP         := '$(GNU_INSTALL_ROOT)/bin/x86_64-w64-mingw32-objdump'
OBJCOPY         := '$(GNU_INSTALL_ROOT)/bin/x86_64-w64-mingw32-objcopy'
SIZE            := '$(GNU_INSTALL_ROOT)/bin/x86_64-w64-mingw32-size'

THIS_DIR          := $(shell dirname $(abspath $(lastword $(MAKEFILE_LIST))))
OUT               := $(abspath $(THIS_DIR))/_build

#DEBUG_FLAGS = -O0 -g3
CFLAGS += -std=c99 -fno-builtin -mwin32 -mwindows -mdll -DKBSIM -D__GNUC_PYTHON__
CFLAGS += $(SML_FLAGS) -DADD_EXPORTS -D_WIN32

LDFLAGS += -L/include -L./
IFLAGS += -I/include
LDLIBS += -lm

// FILL_TENSORFLOW_BUILD_FLAGS

SRCS = $(wildcard *.c)
OBJS = $(patsubst %.c,$(OUT)/%.o,$(SRCS))

// FILL_MAKEFILE_DLL_LIBRARY_NAME_MAIN

$(OUT)/%.o:$(THIS_DIR)/%.c
	@echo $(ANSI_RED)"[cPP]"$(ANSI_OFF) $@
	$(AT)$(CXX) $(CFLAGS) $(IFLAGS) $(LDFLAGS) -fPIC -c -o $@ $< $(LDLIBS)

$(MAIN): $(OBJS)
	@echo $(LDFLAGS)
	$(AT)$(CXX) $(OBJS) -I./ -L./ -Wl,-L. -Wall -mwindows -mdll -Wl,--enable-auto-import -Wl,--out-implib,libsensiml.a -Wl,-d library_exports.def --static -static-libgcc -static-libstdc++ -Wl,--enable-auto-image-base $(LDLIBS)  -o $(MAIN)

clean:
	@echo $(ANSI_RED)"[CLEAN]"$(ANSI_OFF) $@
	rm -f $(OBJS) $(MAIN)

main:  $(MAIN)

all:    main


.PHONY: main all clean
