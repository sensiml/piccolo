
THIS_DIR          := $(shell dirname $(abspath $(lastword $(MAKEFILE_LIST))))
OUT               := $(abspath $(THIS_DIR))

ifndef TF_MICRO_INCLUDE_PATH
TF_MICRO_LIB_PATH =  ./libtfmicro/
TF_MICRO_INCLUDE_PATH = ./libtfmicro/include
endif
ifndef SENSIML_SDK_PATH
SENSIML_SDK_PATH = ../../
endif
ifndef SENSIML_COMMON_PATH
SENSIML_COMMON_PATH = ../../../server/codegen/templates/common
endif

IFLAGS := -I../include -I. -I$(SENSIML_SDK_PATH)include -I$(SENSIML_COMMON_PATH) -I$(TF_MICRO_INCLUDE_PATH)
LFLAGS := -L$(TF_MICRO_LIB_PATH)/libtensorflow-microlite.a
CFLAGS += -std=c99 -fPIC -fno-builtin $(IFLAGS) $(SMLFLAGS) $(LFLAGS) $(ARMFLAGS)

fgsrc_main_path :=
fgsrc_main := tf_micro.c \


fgsrc_path := ./build/
fgsrc := \
	tf_micro.c \
	$(fgsrc_dep)


fgsrc_full := $(addprefix $(fgsrc_path), $(fgsrc))
fgsrc_main_full := $(addprefix $(fgsrc_main_path), $(fgsrc_main))
fgsrc_dep_full := $(addprefix $(fgsrc_dep_path), $(fgsrc_dep))
fgobjs_full := $(patsubst %.c, %.o, $(fgsrc_full))
fgobjs_local := $(patsubst %.c, %.o, $(fgsrc))


SRC := $(fgsrc_full)
OBJS := $(patsubst %.c, %.o, $(fgobjs_local))
COBJS := $(patsubst %.c, %.o, $(SRC))

LIB = $(OUT)/libtfmicroclassifier.so

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
	$(AT)$(CC) -shared -Wl,-o libtfmicroclassifier.so ./build/*.o


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

