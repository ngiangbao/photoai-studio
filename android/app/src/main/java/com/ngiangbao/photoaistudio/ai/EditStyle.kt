package com.ngiangbao.photoaistudio.ai

/**
 * ai/EditStyle.kt - Dinh nghia cac phong cach chinh sua va prompt tuong ung gui cho Gemini.
 *
 * Kotlin port of the desktop app's ai/styles.py. `key` and `prompt` are kept identical to the
 * desktop version so both platforms produce the same edits. The prompt text stays in
 * Vietnamese on purpose - it is the instruction sent to the Gemini model, not UI text, so it
 * does not need to follow the app's display language. The user-facing label lives in
 * strings.xml instead (see ui/StyleLabels.kt) so it can show in either Vietnamese or English.
 */
data class EditStyle(
    val key: String,
    val prompt: String,
)

object Styles {
    val ALL: List<EditStyle> = listOf(
        EditStyle(
            key = "portrait",
            prompt = "Hay chinh sua anh chan dung nay mot cach chuyen nghiep: lam min da tu nhien " +
                "(khong lam mat ket cau da that), can bang tong mau da, lam noi bat doi mat, " +
                "tang nhe do sac net o khuon mat, lam mo nhe hau canh theo kieu chup ong kinh " +
                "khau do lon (bokeh) neu phu hop, anh sang am va de chiu. Giu nguyen danh tinh " +
                "va dac diem khuon mat cua nguoi trong anh, khong thay doi cau truc guong mat.",
        ),
        EditStyle(
            key = "outdoor",
            prompt = "Hay chinh sua anh chup ngoai canh nay: can bang sang/toi tu nhien, tang nhe do " +
                "ruc ro cua bau troi va cay coi mot cach chan thuc (khong qua da), dieu chinh " +
                "can bang trang cho dung voi anh sang tu nhien, tao cam giac dien anh nhe nhang " +
                "nhung van tu nhien, giu nguyen bo cuc va chu the trong anh.",
        ),
        EditStyle(
            key = "landscape",
            prompt = "Hay chinh sua anh phong canh nay theo phong cach nhiep anh thien nhien chuyen " +
                "nghiep: tang dai tuong phan dong (dynamic range), lam bau troi va may ro net " +
                "hon, tang do sau mau sac mot cach chan thuc, lam noi bat chi tiet o tien canh " +
                "va hau canh, sac net vua phai, khong chinh sua qua muc lam mat tinh tu nhien.",
        ),
        EditStyle(
            key = "people",
            prompt = "Hay chinh sua anh chup nguoi nay theo phong cach tu nhien, doi thuong: can " +
                "bang mau da chuan voi nhieu nguoi trong anh, chinh sang deu, giu mau sac trung " +
                "thuc, lam sach nhe cac chi tiet gay xao nhang o hau canh neu co, giu nguyen " +
                "bieu cam va dang dung tu nhien cua moi nguoi.",
        ),
        EditStyle(
            key = "graduation",
            prompt = "Hay chinh sua anh ky yeu/tot nghiep nay: tong mau tuoi sang, ruc ro, vui tuoi, " +
                "dong nhat ve tong mau de phu hop khi ghep chung voi cac anh ky yeu khac, lam " +
                "noi bat nu cuoi va anh sang tren khuon mat, mau sac dong phuc/ao cu nhan ro " +
                "net, co the them chut vignette nhe o vien anh cho noi bat chu the.",
        ),
    )

    val BY_KEY: Map<String, EditStyle> = ALL.associateBy { it.key }
}
