#include <jni.h>
#include <android/log.h>
#include "jni/JniHelper.h"
#include <string>
#include <vector>
using namespace std;
using namespace cocos2d;

string getProjSearchPath()
{
	extern std::string getPackageNameJNI();
	string searchPath = "/mnt/sdcard/";
	searchPath += getPackageNameJNI();
	return searchPath;
}

vector<string> getSearchPath()
{
	extern std::string getPackageNameJNI();
	vector<string> searchPathArray;
	searchPathArray.push_back(getProjSearchPath());
	return searchPathArray;
}

string getDotWaitFilePath()
{
	extern std::string getPackageNameJNI();
	string searchPath = getPackageNameJNI();
	string dotwaitFile = "/mnt/sdcard/";
	dotwaitFile += searchPath;
	dotwaitFile += "/.wait";
	return dotwaitFile;
}

string getSDCardPath()
{
	JniMethodInfo t;
    string sdcardPath("");

    if (JniHelper::getStaticMethodInfo(t, "org/cocos2dx/javascript/Cocos2dxActivity", "getSDCardPath", "()Ljava/lang/String;")) {
        jstring str = (jstring)t.env->CallStaticObjectMethod(t.classID, t.methodID);
        t.env->DeleteLocalRef(t.classID);
        sdcardPath = JniHelper::jstring2string(str);
        t.env->DeleteLocalRef(str);
    }
    return sdcardPath;

}

string getIPAddress()
{
	JniMethodInfo t;
    string IPAddress("");

    if (JniHelper::getStaticMethodInfo(t, "org/cocos2dx/javascript/Cocos2dxActivity", "getLocalIpAddress", "()Ljava/lang/String;")) {
        jstring str = (jstring)t.env->CallStaticObjectMethod(t.classID, t.methodID);
        t.env->DeleteLocalRef(t.classID);
        IPAddress = JniHelper::jstring2string(str);
        t.env->DeleteLocalRef(str);
    }
    return IPAddress;
}
