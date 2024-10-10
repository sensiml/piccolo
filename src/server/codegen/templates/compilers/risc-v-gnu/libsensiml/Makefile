GNU_PREFIX := riscv32-unknown-elf

ADD_FEATURE_VECTOR?=y
ADD_SEGMENT_DATA?=n
BUILD_TENSORFLOW?=n

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

# CPU_TYPE=cortex-m4
CPU_TYPE=
FLOAT_TYPE=auto
FLOAT_HARDWARE=hard


# Toolchain commands
CC              := '$(GNU_PREFIX)-gcc'
AS              := '$(GNU_PREFIX)-as'
AR              := '$(GNU_PREFIX)-ar' -r
LD              := '$(GNU_PREFIX)-ld'
NM              := '$(GNU_PREFIX)-nm'
OBJDUMP         := '$(GNU_PREFIX)-objdump'
OBJCOPY         := '$(GNU_PREFIX)-objcopy'
SIZE            := '$(GNU_PREFIX)-size'

THIS_DIR          := $(shell dirname $(abspath $(lastword $(MAKEFILE_LIST))))
OUT               := $(abspath $(THIS_DIR))/_build


#DEBUG_FLAGS = -O0 -g3
CFLAGS += -std=gnu99 -Os -g3 -MMD -c -mlongcalls
CFLAGS += $(CPU_TYPE)
CFLAGS += $(SML_FLAGS)


LDFLAGS += -L/include
IFLAGS += -I/include -I./
LDLIBS += -lm


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


