# FP加解密工具使用方式

## Usage
可以使用短option，也可使用长option，传入参数时可以使用`<option>=<param>`的方式，也可以使用`<option> <param>`的方式传入。
```shell
usage: java -jar fp-enc-tool.jar <-d|-e> -k=<key_path> -s=<source_file_path>
 -d,--decode                      encrypt mode
 -e,--encode                      decrypt mode
 -f,--fpEncode <fpEncodeNum>      set fpEncode type. [3、4、7、8、web、weapp]
 -h,--help                        show help
 -k,--key <key_dir_path>          public & private key dir path.
 -o,--org <org>                   organization.
 -s,--source <source_file_path>   The path of source string file.
```

## Example
- FpEncode=3，加密Android。

    ```
    java -jar fp-enc-tool.jar -e -f=3 -o=IkzxwQ4vofwwvFqC8ir2 -s=source_file_path
    ```

- FpEncode=3，解密Android。

    ```
    java -jar fp-enc-tool.jar -d -f=3 -o=IkzxwQ4vofwwvFqC8ir2 -s=source_file_path
    ```

- FpEncode=4，加密iOS。

    ```
    java -jar fp-enc-tool.jar -e -f=4 -o=IkzxwQ4vofwwvFqC8ir2 -s=source_file_path
    ```

- FpEncode=4，解密iOS。

    ```
    java -jar fp-enc-tool.jar -e -f=4 -o=IkzxwQ4vofwwvFqC8ir2 -s=source_file_path
    ```

- FpEncode=7，加密Android。

    ```
    java -jar fp-enc-tool.jar -e -f=7 -o=IkzxwQ4vofwwvFqC8ir2 -k=key_files_dir -s=source_file_path
    ```

- FpEncode=7，解密Android。

    ```
    java -jar fp-enc-tool.jar -e -f=7 -k=key_files_dir -s=source_file_path
    ```

- FpEncode=8，加密iOS。

    ```
    java -jar fp-enc-tool.jar -e -f=8 -o=IkzxwQ4vofwwvFqC8ir2 -k=key_files_dir -s=source_file_path
    ```

- FpEncode=8，解密iOS。

    ```
    java -jar fp-enc-tool.jar -e -f=8 -k=key_files_dir -s=source_file_path
    ```
    
- 加密Web。

    ```
    java -jar fp-enc-tool.jar -e -f=web -o=IkzxwQ4vofwwvFqC8ir2 -s=source_file_path
    ```
    
- 解密Web。

    ```
    java -jar fp-enc-tool.jar -d -f=web -s=source_file_path
    ```
    
- 加密Weapp。

    ```
    java -jar fp-enc-tool.jar -e -f=weapp -o=IkzxwQ4vofwwvFqC8ir2 -s=source_file_path
    ```
    
- 解密Weapp。

    ```
    java -jar fp-enc-tool.jar -d -f=weapp -s=source_file_path
    ```


## 注意事项
1. -d、-e参数必须传入一个。
2. 选择加密时需要传入org。
3. fpEncode为3、4时，加解密都需要传入org。fpEncode为7、8时需要传入key。
4. 以上参数传入不正确时，会打印提示。
5. 传入的source_file支持多行，会一行一行进行加密/解密输出，但注意文件不要过大。