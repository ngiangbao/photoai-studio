"""
ai/styles.py - Dinh nghia cac phong cach chinh sua va prompt tuong ung gui cho Gemini
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class EditStyle:
    key: str
    label: str
    prompt: str


STYLES = [
    EditStyle(
        key="portrait",
        label="Chan dung",
        prompt=(
            "Hay chinh sua anh chan dung nay mot cach chuyen nghiep: lam min da tu nhien "
            "(khong lam mat ket cau da that), can bang tong mau da, lam noi bat doi mat, "
            "tang nhe do sac net o khuon mat, lam mo nhe hau canh theo kieu chup ong kinh "
            "khau do lon (bokeh) neu phu hop, anh sang am va de chiu. Giu nguyen danh tinh "
            "va dac diem khuon mat cua nguoi trong anh, khong thay doi cau truc guong mat."
        ),
    ),
    EditStyle(
        key="outdoor",
        label="Ngoai canh",
        prompt=(
            "Hay chinh sua anh chup ngoai canh nay: can bang sang/toi tu nhien, tang nhe do "
            "ruc ro cua bau troi va cay coi mot cach chan thuc (khong qua da), dieu chinh "
            "can bang trang cho dung voi anh sang tu nhien, tao cam giac dien anh nhe nhang "
            "nhung van tu nhien, giu nguyen bo cuc va chu the trong anh."
        ),
    ),
    EditStyle(
        key="landscape",
        label="Phong canh",
        prompt=(
            "Hay chinh sua anh phong canh nay theo phong cach nhiep anh thien nhien chuyen "
            "nghiep: tang dai tuong phan dong (dynamic range), lam bau troi va may ro net "
            "hon, tang do sau mau sac mot cach chan thuc, lam noi bat chi tiet o tien canh "
            "va hau canh, sac net vua phai, khong chinh sua qua muc lam mat tinh tu nhien."
        ),
    ),
    EditStyle(
        key="people",
        label="Chup nguoi / doi thuong",
        prompt=(
            "Hay chinh sua anh chup nguoi nay theo phong cach tu nhien, doi thuong: can "
            "bang mau da chuan voi nhieu nguoi trong anh, chinh sang deu, giu mau sac trung "
            "thuc, lam sach nhe cac chi tiet gay xao nhang o hau canh neu co, giu nguyen "
            "bieu cam va dang dung tu nhien cua moi nguoi."
        ),
    ),
    EditStyle(
        key="graduation",
        label="Chup ky yeu",
        prompt=(
            "Hay chinh sua anh ky yeu/tot nghiep nay: tong mau tuoi sang, ruc ro, vui tuoi, "
            "dong nhat ve tong mau de phu hop khi ghep chung voi cac anh ky yeu khac, lam "
            "noi bat nu cuoi va anh sang tren khuon mat, mau sac dong phuc/ao cu nhan ro "
            "net, co the them chut vignette nhe o vien anh cho noi bat chu the."
        ),
    ),
]

STYLES_BY_KEY = {s.key: s for s in STYLES}
