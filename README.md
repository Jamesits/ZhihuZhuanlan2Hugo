# ZhihuZhuanlan2Hugo

Convert Zhihu Zhuanlan (知乎专栏) to Hugo static site.

Daily CI: [![Build status](https://dev.azure.com/nekomimiswitch/Zhihu%20Zhuanlan/_apis/build/status/Zhihu%20Zhuanlan%20Backup%20Task)](https://dev.azure.com/nekomimiswitch/Zhihu%20Zhuanlan/_build/latest?definitionId=36)

Sample site: https://zhuanlan.swineson.me/

## Usage

```shell
./main.py column_name1 [column_name2 [column_name3 [...]]] destination_folder
```

Destination folder should be a root folder of a Hugo site. This program will expect a `content` subfolder inside it.

We recommend using the [Zhihu Zhuanlan theme](https://github.com/Jamesits/hugo-theme-ZhihuZhuanlan).
