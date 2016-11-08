#!/bin/bash

. shellscripts/querylibrary.sh # import custom functions

getstableFClist
printf "StableFCParameterCount:`summarystableFCs`"