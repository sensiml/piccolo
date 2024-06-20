

GNU_PREFIX := arm-none-linux-gnueabihf

ADD_FEATURE_VECTOR?=y
ADD_SEGMENT_DATA?=n
BUILD_TENSORFLOW?=n

SML_FLAGS += -DKB_USE_SW_PME -DKBSIM

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

# CPU_TYPE=cortex-m4
FLOAT_TYPE=auto
FLOAT_HARDWARE=soft
// FILL_CPU_TYPE
// FILL_FLOAT_TYPE
// FILL_FLOAT_HARDWARE


# Toolchain commands
CC              := '$(GNU_INSTALL_ROOT)/bin/$(GNU_PREFIX)-gcc'
CXX              := '$(GNU_INSTALL_ROOT)/bin/$(GNU_PREFIX)-g++'
AS              := '$(GNU_INSTALL_ROOT)/bin/$(GNU_PREFIX)-as'
AR              := '$(GNU_INSTALL_ROOT)/bin/$(GNU_PREFIX)-ar' -r
LD              := '$(GNU_INSTALL_ROOT)/bin/$(GNU_PREFIX)-ld'
NM              := '$(GNU_INSTALL_ROOT)/bin/$(GNU_PREFIX)-nm'
OBJDUMP         := '$(GNU_INSTALL_ROOT)/bin/$(GNU_PREFIX)-objdump'
OBJCOPY         := '$(GNU_INSTALL_ROOT)/bin/$(GNU_PREFIX)-objcopy'
SIZE            := '$(GNU_INSTALL_ROOT)/bin/$(GNU_PREFIX)-size'

THIS_DIR          := $(shell dirname $(abspath $(lastword $(MAKEFILE_LIST))))
OUT               := $(abspath $(THIS_DIR))/_build

#DEBUG_FLAGS = -O0 -g3
CFLAGS += -std=c99 -fno-builtin -nostdlib -nodefaultlibs -ffreestanding -nostartfiles -fPIC
CFLAGS += $(CPU_TYPE) -mthumb -mfpu=$(FLOAT_TYPE) -mfloat-abi=$(FLOAT_HARDWARE)
CFLAGS += $(SML_FLAGS)

LDFLAGS += -L/include
IFLAGS += -I/include
LDLIBS += -lm


// FILL_TENSORFLOW_BUILD_FLAGS

SRCS = $(wildcard *.c)
OBJS = $(patsubst %.c,$(OUT)/%.o,$(SRCS))

MAIN = $(OUT)/libsensiml.a

$(OUT)/%.o:$(THIS_DIR)/%.c
		@echo $(ANSI_RED)"[cPP]"$(ANSI_OFF) $@
		$(AT)$(CC) $(CFLAGS) $(IFLAGS) $(LDFLAGS) -c -o $@ $< $(LDLIBS)


$(MAIN): $(OBJS)
		@echo $(LDFLAGS)
	        $(AR) -cs $(MAIN) $(OBJS)

clean:
		@echo $(ANSI_RED)"[CLEAN]"$(ANSI_OFF) $@
		rm -f $(OBJS) $(LIB)

main:  $(MAIN)

all:	main


.PHONY:	main all clean
