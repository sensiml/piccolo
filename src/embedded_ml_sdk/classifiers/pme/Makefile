
THIS_DIR          := $(shell dirname $(abspath $(lastword $(MAKEFILE_LIST))))
OUT               := $(abspath $(THIS_DIR))

ifndef SENSIML_SDK_PATH
SENSIML_SDK_PATH = ../../
endif
ifndef SENSIML_COMMON_PATH
SENSIML_COMMON_PATH = ../../../server/codegen/templates/common
endif

IFLAGS := -I../include -I. -I$(SENSIML_SDK_PATH)include -I$(SENSIML_COMMON_PATH)
SMLFLAGS := -DENABLE_DTW_DISTANCE
CFLAGS += -std=c99 -fPIC -fno-builtin $(IFLAGS) $(SMLFLAGS)

fgsrc_dep_path :=$(SENSIML_SDK_PATH)src/
fgsrc_dep := \
	dsp_l1_distance.c \
	dsp_lsup_distance.c \
	dsp_dtw_distance.c \
	utils_bitwise_abs_val.c \
	utils_array_max_uint8.c

fgsrc_main_path :=
fgsrc_main := pme.c


fgsrc_path := ./build/
fgsrc := \
	pme.c \
	$(fgsrc_dep)


fgsrc_full := $(addprefix $(fgsrc_path), $(fgsrc))
fgsrc_main_full := $(addprefix $(fgsrc_main_path), $(fgsrc_main))
fgsrc_dep_full := $(addprefix $(fgsrc_dep_path), $(fgsrc_dep))
fgobjs_full := $(patsubst %.c, %.o, $(fgsrc_full))
fgobjs_local := $(patsubst %.c, %.o, $(fgsrc))


SRC := $(fgsrc_full)
OBJS := $(patsubst %.c, %.o, $(fgobjs_local))
COBJS := $(patsubst %.c, %.o, $(SRC))

LIB = $(OUT)/libpmeclassifier.so

define copyofiles
#   ex1 := $(foreach of1,$(srcofiles1),cp -f $(of1) src/ &&)
#   ex1 += $(foreach of2,$(srcofiles2),cp -f $(of2) src/embedded_ml_sdk/ &&)
	rm -rf ./build
	mkdir build

    for of1 in $(fgsrc_main_full); do \
        cp $$of1 ./build; \
    done

	echo $(fgsrc_dep_full)

    for of1 in $(fgsrc_dep_full); do \
        cp $$of1 ./build; \
    done

endef


$(LIB): $(COBJS)
	@echo $(LDFLAGS)
	$(AT)$(AR) -rcs $@ $(COBJS)
	$(AT)$(CC) -shared -Wl,-o libpmeclassifier.so ./build/*.o


clean:
	@echo $(ANSI_RED)"[CLEAN]"$(ANSI_OFF) $@
	@echo $(SRC)
	rm -f $(OBJS) $(LIB)
	rm -f *.so
	rm -rf ./build

setup:
	$(call copyofiles)

install:
	cp $(LIB) $(INSTALL_PATH)

all: setup
	 $(LIB)

.PHONY:	lib all clean installofiles

