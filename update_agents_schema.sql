-- =================================================================
-- Agents 테이블 API 정보 컬럼 업데이트
-- =================================================================

-- 1단계: 기존 컬럼 타입 확인 및 수정
DO $$
BEGIN
    -- api_id 컬럼이 문자열인 경우 정수로 변경
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'agents' 
        AND column_name = 'api_id' 
        AND data_type = 'character varying'
    ) THEN
        -- 기존 데이터 백업
        CREATE TEMP TABLE agents_backup AS SELECT * FROM agents;
        
        -- api_id 컬럼 타입 변경
        ALTER TABLE agents ALTER COLUMN api_id TYPE INTEGER USING 
            CASE 
                WHEN api_id ~ '^[0-9]+$' THEN api_id::INTEGER
                ELSE 25060740  -- 기본값
            END;
            
        RAISE NOTICE 'api_id 컬럼을 INTEGER로 변경했습니다.';
    END IF;
    
    -- api_hash 컬럼이 없는 경우 추가
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'agents' 
        AND column_name = 'api_hash'
    ) THEN
        ALTER TABLE agents ADD COLUMN api_hash VARCHAR(255);
        RAISE NOTICE 'api_hash 컬럼을 추가했습니다.';
    END IF;
    
END $$;

-- 2단계: 기본값 설정
UPDATE agents 
SET 
    api_id = COALESCE(api_id, 25060740),
    api_hash = COALESCE(api_hash, 'f93d24a5fba99007d0a81a28ab5ca7bc')
WHERE api_id IS NULL OR api_hash IS NULL;

-- 3단계: 제약 조건 추가
ALTER TABLE agents 
ALTER COLUMN api_id SET NOT NULL,
ALTER COLUMN api_hash SET NOT NULL;

-- 4단계: 인덱스 추가 (선택사항)
CREATE INDEX IF NOT EXISTS idx_agents_api_info ON agents(api_id, api_hash);

-- 완료 메시지
SELECT '✅ Agents 테이블 API 정보 업데이트 완료' as status; 