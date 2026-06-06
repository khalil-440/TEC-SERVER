#!/bin/bash

ps -eo pid,user,%cpu,%mem,comm --sort=-%cpu | head -20
