P2P DOSYA AKTARIMI / P2P FILE TRANSFER
======================================

DOSYAYI KAYNAKTAN CALISTIRMA / RUN FROM SOURCE
1. Python 3.11+ kurun / Install Python 3.11+.
2. Terminalde / In a terminal:
   python -m pip install --upgrade "magic-wormhole>=0.23.0"
3. Uygulamayi calistirin / Run the app:
   python kolay_dosya_aktarimi_duzeltilmis.py

WINDOWS EXE OLUSTURMA / BUILD WINDOWS EXE
1. Bu klasoru Windows bilgisayarina kopyalayin.
2. build_windows.bat dosyasina cift tiklayin. Betik bozuk genel `py` secimini kullanmamak icin once calisan `python` komutunu dener; gerekirse Python 3.14, 3.13, 3.12 veya 3.11 launcher seceneklerini dener.
   Desteklenen bir Python kurulumunuz yoksa python.org uzerinden Python 3.11-3.14 kurup PATH secenegini etkinlestirin.
3. Olusan uygulama: dist\P2P-File-Transfer.exe

NOT / NOTE
Bu derleme betigi Windows ortaminda calistirilmalidir; bu Linux ortamindan
Windows PE .exe dosyasi dogrudan derlenemedi. Uygulama Magic Wormhole CLI'sini
kullanir; hedef bilgisayarda Python ve magic-wormhole paketi de bulunmalidir.
Aktarimlar Magic Wormhole protokolunu kullanir. Baglanti kosullarina gore
aktarim dogrudan esler arasinda veya yardimci relay altyapisi uzerinden olabilir;
her agda yalnizca dogrudan P2P baglanti garantisi verilmez.

The build script must be run on Windows. A Windows PE .exe could not be built
in this Linux environment. The script avoids using a broken generic `py` launcher
entry by testing `python` first, then trying Python 3.14, 3.13, 3.12, and 3.11 explicitly. The app invokes the Magic Wormhole CLI, so Python
and magic-wormhole must also be installed on the target PC. Depending on network
conditions, connections may be direct peer-to-peer or use relay infrastructure;
a direct-only connection is not guaranteed on every network.
