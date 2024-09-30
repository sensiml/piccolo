GNU_INSTALL_ROOT := /usr

ADD_FEATURE_VECTOR?=y
ADD_SEGMENT_DATA?=n
ADD_SEGMENT_DATA?=n

SML_FLAGS := 

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
CC              := '$(GNU_INSTALL_ROOT)/bin/gcc'
CXX              := '$(GNU_INSTALL_ROOT)/bin/g++'
AS              := '$(GNU_INSTALL_ROOT)/bin/as'
AR              := '$(GNU_INSTALL_ROOT)/bin/ar' -r
LD              := '$(GNU_INSTALL_ROOT)/bin/ld'
NM              := '$(GNU_INSTALL_ROOT)/bin/nm'
OBJDUMP         := '$(GNU_INSTALL_ROOT)/bin/objdump'
OBJCOPY         := '$(GNU_INSTALL_ROOT)/bin/objcopy'
SIZE            := '$(GNU_INSTALL_ROOT)/bin/size'

THIS_DIR          := $(shell dirname $(abspath $(lastword $(MAKEFILE_LIST))))
OUT               := $(abspath $(THIS_DIR))/_build

DEBUG_FLAGS = -O0 -g3 -fpermissive -Wnarrowing
CXXFLAGS += -fno-builtin -DKBSIM -D__GNUC_PYTHON__ 
CXXFLAGS += $(SML_FLAGS)

LDFLAGS += -L/include -L./
IFLAGS += -I/include -I/layers -I./
LDLIBS += -lm

// FILL_TENSORFLOW_BUILD_FLAGS

SRCS = $(wildcard *.c)
OBJS = $(patsubst %.c,$(OUT)/%.o,$(SRCS))


// FILL_MAKEFILE_LIBRARY_NAME_MAIN

#$(OUT)/%.o:$(THIS_DIR)/%.c
#		@echo $(ANSI_RED)"[cPP]"$(ANSI_OFF) $@
#		$(AT)$(CXX) $(CXXFLAGS) $(IFLAGS) $(LDFLAGS) -fPIC -c -o $@ $< $(LDLIBS)


$(OUT)/%.o:$(THIS_DIR)/%.c
		@echo $(ANSI_RED)"[cPP]"$(ANSI_OFF) $@
		$(AT)$(CC) $(CXXFLAGS) $(IFLAGS) $(LDFLAGS) -fPIC -c -o $@ $< $(LDLIBS)


$(MAIN): $(OBJS)
		@echo $(LDFLAGS)
	        $(AR) -cs $(MAIN) $(OBJS)

clean:
		@echo $(ANSI_RED)"[CLEAN]"$(ANSI_OFF) $@
		rm -f $(OBJS) $(LIB)

main:  $(MAIN)

all:	main


.PHONY:	main all clean
