class ChainValidator:
    """
    Zincir doğrulama işlemlerini yürüten statik sınıf.
    """
    
    @staticmethod
    def validate_chain(records):
        """
        Veritabanındaki kayıtları (liste halinde dict veya sqlite3.Row) alır ve zinciri doğrular.
        """
        broken_indices = []
        
        # Kayıt yoksa veya tek kayıt varsa geçerli say
        if not records:
            return {"is_valid": True, "broken_indices": []}

        # Döngüye 1. indexten başlıyoruz (Genesis'i atla)
        for i in range(1, len(records)):
            current_record = records[i]
            previous_record = records[i-1]
            
            # .get() yerine [] kullanıyoruz (sqlite3.Row uyumluluğu için)
            try:
                # Bir önceki kaydın hash'i
                expected_prev_hash = previous_record["file_hash"]
                
                # Şu anki kaydın iddia ettiği 'prev_hash'
                actual_prev_hash = current_record["prev_hash"]
                
                # Zincir Kontrolü
                if expected_prev_hash != actual_prev_hash:
                    broken_indices.append(current_record["id"])
                    
            except (KeyError, IndexError, TypeError):
                # Eğer veri yapısında bir bozukluk varsa bunu da hata sayabiliriz
                # Şimdilik güvenli tarafta kalıp o kaydı işaretliyoruz
                broken_indices.append(current_record["id"] if "id" in current_record else i)

        is_valid = len(broken_indices) == 0
        
        return {
            "is_valid": is_valid,
            "broken_indices": broken_indices
        }