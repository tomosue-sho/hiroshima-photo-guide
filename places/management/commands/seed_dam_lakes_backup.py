from django.core.management.base import BaseCommand
from places.models import DamLake

DAM_LAKES = [
    (1, "富里湖", "富里ダム", "北海道", "tomisato"),
    (2, "聖台ダム公園", "聖台ダム", "北海道", "seidai"),
    (3, "かなやま湖", "金山ダム", "北海道", "kanayama"),
    (4, "定山湖", "豊平峡ダム", "北海道", "jozanko"),
    (5, "笹流貯水池", "笹流ダム", "北海道", "sasaarashi"),
    (6, "かわうち湖", "川内ダム", "青森県", "kawauchi"),
    (7, "岩洞湖", "岩洞ダム", "岩手県", "gando"),
    (8, "御所湖", "御所ダム", "岩手県", "gosho"),
    (9, "田瀬湖", "田瀬ダム", "岩手県", "tase"),
    (10, "錦秋湖", "湯田ダム", "岩手県", "kinshuko"),
    (11, "七ッ森湖", "南川ダム", "宮城県", "nanatsumoriko"),
    (12, "あさひな湖", "宮床ダム", "宮城県", "asahinako"),
    (13, "釜房湖", "釜房ダム", "宮城県", "kamafusa"),
    (14, "七ヶ宿湖", "七ヶ宿ダム", "宮城県", "shichikashuku"),
    (15, "宝仙湖", "玉川ダム", "秋田県", "hosenko"),
    (16, "月山湖", "寒河江ダム", "山形県", "gassan"),
    (17, "羽鳥湖", "羽鳥ダム", "福島県", "hatori"),
    (18, "田子倉湖", "田子倉ダム", "福島県", "tagokura"),
    (19, "銀山湖", "奥只見ダム", "福島県", "ginzan"),
    (20, "奥利根湖", "矢木沢ダム", "群馬県", "okutone"),
    (21, "ならまた湖", "奈良俣ダム", "群馬県", "naramata"),
    (22, "野反湖", "野反ダム", "群馬県", "nozoriko"),
    (23, "赤谷湖", "相俣ダム", "群馬県", "akatani"),
    (24, "草木湖", "草木ダム", "群馬県", "kusaki"),
    (25, "神流湖", "下久保ダム", "群馬県・埼玉県", "kannako"),
    (26, "狭山湖", "山口貯水池ダム", "埼玉県", "sayamako"),
    (27, "多摩湖", "村山下ダム", "東京都", "tamako"),
    (28, "奥多摩湖", "小河内ダム", "東京都", "okutamako"),
    (29, "宮ヶ瀬湖", "宮ヶ瀬ダム", "神奈川県", "miyagase"),
    (30, "丹沢湖", "三保ダム", "神奈川県", "tanzawa"),
    (31, "黒部湖", "黒部ダム", "富山県", "kurobe"),
    (32, "有峰湖", "有峰ダム", "富山県", "arimine"),
    (33, "高瀬ダム調整湖", "高瀬ダム", "長野県", "takase"),
    (34, "奥木曽湖", "味噌川ダム", "長野県", "okukiso"),
    (35, "高遠湖", "高遠ダム", "長野県", "takatoko"),
    (36, "美和湖", "美和ダム", "長野県", "miwako"),
    (37, "恵那峡", "大井ダム", "岐阜県", "enakyo"),
    (38, "阿木川湖", "阿木川ダム", "岐阜県", "agigawa"),
    (39, "佐久間湖", "佐久間ダム", "静岡県", "sakuma"),
    (40, "三河湖", "羽布ダム", "愛知県", "mikawako"),
    (41, "永源寺湖", "永源寺ダム", "滋賀県", "eigenji"),
    (42, "虹の湖", "大野ダム", "京都府", "nijinoko"),
    (43, "天若湖", "日吉ダム", "京都府", "ama-waka"),
    (44, "知明湖", "一庫ダム", "兵庫県", "chimyoko"),
    (45, "布引貯水池", "五本松ダム", "兵庫県", "nunobiki"),
    (46, "池原貯水池", "池原ダム", "奈良県", "ikehara"),
    (47, "椿山ダム湖", "椿山ダム", "和歌山県", "tsubakiyama"),
    (48, "神龍湖", "帝釈川ダム", "広島県", "shinryuko"),
    (49, "八千代湖", "土師ダム", "広島県", "yachiyoko"),
    (50, "龍姫湖", "温井ダム", "広島県", "tatsuhimeko"),
    (51, "本庄貯水池", "本庄ダム", "広島県", "honjo"),
    (52, "弥栄湖", "弥栄ダム", "広島県・山口県", "yasaka"),
    (53, "小野湖", "厚東川ダム", "山口県", "onoko"),
    (54, "満濃池", "満濃池ダム", "香川県", "mannou"),
    (55, "朝霧湖", "野村ダム", "愛媛県", "asagiri"),
    (56, "さめうら湖", "早明浦ダム", "高知県", "sameura"),
    (57, "上秋月湖", "江川ダム", "福岡県", "kamiakizuki"),
    (58, "美奈宜湖", "寺内ダム", "福岡県", "minagi"),
    (59, "鷹島ダム淡水湖", "鷹島海中ダム", "長崎県", "takashima"),
    (60, "北川ダム湖", "北川ダム", "大分県", "kitagawa"),
    (61, "日向椎葉湖", "上椎葉ダム", "宮崎県", "hyuga-shiiba"),
    (62, "大鶴湖", "鶴田ダム", "鹿児島県", "otsuru"),
    (63, "福上湖", "福地ダム", "沖縄県", "fukugami"),
    (64, "かんな湖", "漢那ダム", "沖縄県", "kannako-okinawa"),
    (65, "倉敷湖", "倉敷ダム", "沖縄県", "kurashiki-okinawa"),
]


class Command(BaseCommand):
    help = "ダム湖百選65湖の初期データを登録します。"

    def handle(self, *args, **options):

        created_count = 0
        existing_count = 0

        for order, name, dam_name, prefecture, slug in DAM_LAKES:

            lake, created = DamLake.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "dam_name": dam_name,
                    "prefecture": prefecture,
                    "order": order,
                },
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created: {order:02d} {name}"
                    )
                )
            else:
                existing_count += 1
                self.stdout.write(
                    f"Exists: {order:02d} {name}"
                )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"完了: 新規 {created_count} 件 / 既存 {existing_count} 件"
            )
        )

