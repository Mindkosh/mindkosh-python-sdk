# Copyright (C) 2022 Mindkosh Technologies. All rights reserved.
# Author: Parmeshwar Kumawat

from enum import Enum

class ResourceType(Enum):

    LOCAL = 0
    S3 = 1

    def __str__(self):
        return self.name.lower()

    def __repr__(self):
        return str(self)