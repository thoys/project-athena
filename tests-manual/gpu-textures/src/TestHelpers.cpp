//
//  Created by Bradley Austin Davis on 2016/05/16
//  Copyright 2014 High Fidelity, Inc.
//
//  Distributed under the Apache License, Version 2.0.
//  See the accompanying file LICENSE or http://www.apache.org/licenses/LICENSE-2.0.html
//

#include "TestHelpers.h"
#include <QtCore/QFileInfo>

QString projectRootDir() {
    static QString projectRootPath = QFileInfo(QFileInfo(__FILE__).absolutePath() + "/..").absoluteFilePath();
    return projectRootPath;
}
