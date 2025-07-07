1：fuzzware_harness emulator -h 可以查看到可以选择的参数
	--default_yml DEFAULT_YML
	--svd_path SVD_PATH

这两个参数的选择可以进行svd文件的处理个yml文件的选择

2：其他使用方法保留和原始的一样，没有做过多的修改

3：可以参考下面原始使用方法
工作流程：

配置目标映像（fuzzware genconfig ）
模糊目标： fuzzware pipeline --run-for 24:00:00
收集覆盖统计信息： fuzzware genstats coverage
在 fuzzware-project/stats中找到您的覆盖信息
如果你想从Fuzzware中得到最好的（作为一个人在循环中），查看以下步骤：

构建或获取目标固件映像
配置基本内存范围：手动创建config或使用 fuzzware genconfig （最适合elf文件，但仍然对输出持保留意见并手动验证！）

模糊目标： fuzzware pipeline
检查覆盖率: fuzzware cov ,  fuzzware cov -o cov.txt 和 fuzzware cov <target_function> ,  fuzzware replay --covering <target_function>

调整配置：fuzzware-emulator/README_config。又是Yml和fuzz。如果镜像需要重新构建，请转到步骤1。如果需要调整配置，请转到步骤3。
一旦您合理地确定在当前设置中达到了有意义的功能，那么扩展内核： fuzzware pipeline -n 16 可能是有意义的。

检查崩溃： fuzzware genstats crashcontexts
重放和分析崩溃： fuzzware replay -M -t mainXXX/fuzzers/fuzzerY/crashes/idZZZ
查看崩溃的位置：ls fuzzware-project/main*/fuzzers/fuzzer*/crashes/id* 或者可以使用fuzzware genstats crashcontexts

fuzzware cov --outfile cov.txt 输出覆盖范围到指定文件

fuzzware genstats coverage --valid-bb-file cov.txt 输出cov.txt统计输出

虚拟机挂载共享目录的命令
sudo mount -t fuse.vmhgfs-fuse .host:/ /mnt/hgfs -o allow_other
