"""
Database Seeder Script.
Populates the database with initial demo operator and realistic lead records.
Usage:
    python seed.py
"""
import sys
from app.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.lead import Lead, LeadStatus
from app.models.activity import LeadActivity, ActivityAction
from app.services.auth_service import hash_password

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def seed():
    print("[INIT] Baza jadvallari tekshirilmoqda...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Create Demo Admin User
        admin_email = "admin@crm.uz"
        admin = db.query(User).filter(User.email == admin_email).first()
        if not admin:
            admin = User(
                email=admin_email,
                full_name="Abdulaziz Axmadaliev",
                hashed_password=hash_password("admin123"),
                is_active=True
            )
            db.add(admin)
            db.flush()
            print(f"[OK] Demo administrator yaratildi: {admin_email} / admin123")
        else:
            print(f"[INFO] Demo admin allaqachon mavjud: {admin_email}")

        # 2. Check if leads already exist
        if db.query(Lead).count() > 0:
            print("[INFO] Ma'lumotlar bazasida leadlar mavjud. Yangi leadlar qo'shilmadi.")
            return

        print("[INFO] Realistik test leadlari qo'shilmoqda...")
        demo_leads = [
            {
                "name": "Apex Soft Technologies",
                "phone": "+998 90 123 45 67",
                "email": "contact@apexsoft.uz",
                "source": "Website",
                "status": LeadStatus.NEW.value,
                "note": "ERP tizimini joriy qilish bo'yicha veb-sayt orqali so'rov yuborgan."
            },
            {
                "name": "Jasur Rahimov",
                "phone": "+998 93 456 78 90",
                "email": "jasur.r@gmail.com",
                "source": "Telegram",
                "status": LeadStatus.CONTACTED.value,
                "note": "Telegram bot orqali murojaat qilgan. Dastlabki narxlar ro'yxati yuborildi."
            },
            {
                "name": "Global Logistika MChJ",
                "phone": "+998 71 200 11 22",
                "email": "info@globallogistics.uz",
                "source": "Referral",
                "status": LeadStatus.QUALIFIED.value,
                "note": "Mavjud mijoz tavsiyasi bilan kelgan. Byudjet tasdiqlangan, texnik topshiriq kutilmoqda."
            },
            {
                "name": "Fintech Solutions",
                "phone": "+998 97 999 88 77",
                "email": "ceo@fintech.uz",
                "source": "Google Ads",
                "status": LeadStatus.WON.value,
                "note": "Shartnoma imzolandi va 50% avans to'lovi qabul qilindi."
            },
            {
                "name": "Zilola Mahmudova",
                "phone": "+998 99 333 22 11",
                "email": "zilola.m@mail.ru",
                "source": "Instagram",
                "status": LeadStatus.LOST.value,
                "note": "Xizmat narxi qimmatlik qilgani sababli muzokaralar to'xtatildi."
            },
            {
                "name": "Smart Education Markazi",
                "phone": "+998 91 777 55 44",
                "email": "study@smartedu.uz",
                "source": "Website",
                "status": LeadStatus.CONTACTED.value,
                "note": "O'quv markazi uchun avtomatlashtirish kerak. Ertaga soat 15:00 da demo uchrashuv."
            },
            {
                "name": "Eco Food Distribyutsiya",
                "phone": "+998 94 888 12 34",
                "email": "sales@ecofood.uz",
                "source": "Cold Call",
                "status": LeadStatus.NEW.value,
                "note": "Sovuq qo'ng'iroq orqali qiziqish bildirdi. Taqdimot yuborilishi kerak."
            },
            {
                "name": "Orient Building",
                "phone": "+998 78 150 00 99",
                "email": "tender@orientbuilding.uz",
                "source": "Event",
                "status": LeadStatus.QUALIFIED.value,
                "note": "IT EXPO ko'rgazmasida tanishdik. Boshqaruv CRM tizimi kerak."
            },
            {
                "name": "Olimjon Usmonov",
                "phone": "+998 90 321 65 49",
                "email": "olim.u@inbox.uz",
                "source": "Telegram",
                "status": LeadStatus.WON.value,
                "note": "Mini-CRM integratsiyasi muvaffaqiyatli yakunlandi."
            }
        ]

        for lead_data in demo_leads:
            lead = Lead(
                name=lead_data["name"],
                phone=lead_data["phone"],
                email=lead_data["email"],
                source=lead_data["source"],
                status=lead_data["status"],
                note=lead_data["note"],
                owner_id=admin.id
            )
            db.add(lead)
            db.flush()

            # Create initial activity
            activity = LeadActivity(
                lead_id=lead.id,
                user_id=admin.id,
                action=ActivityAction.CREATED.value,
                new_status=lead.status,
                description=f"{admin.full_name} tomonidan '{lead.name}' ({lead.source}) tizimga kiritildi."
            )
            db.add(activity)

            # If status is not New, add status change record
            if lead.status != LeadStatus.NEW.value:
                st_activity = LeadActivity(
                    lead_id=lead.id,
                    user_id=admin.id,
                    action=ActivityAction.STATUS_CHANGED.value,
                    old_status=LeadStatus.NEW.value,
                    new_status=lead.status,
                    description=f"{admin.full_name} lead statusini 'New' dan '{lead.status}' ga o'zgartirdi."
                )
                db.add(st_activity)

        db.commit()
        print(f"[SUCCESS] Muvaffaqiyatli {len(demo_leads)} ta namunaviy lead qo'shildi!")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Xatolik yuz berdi: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed()
