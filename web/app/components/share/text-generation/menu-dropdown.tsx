'use client'
import type { FC } from 'react'
import React, { useCallback, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import type { Placement } from '@floating-ui/react'
import {
  RiEqualizer2Line,
} from '@remixicon/react'
import { usePathname, useRouter } from 'next/navigation'
import Divider from '../../base/divider'
import InfoModal from './info-modal'
import ActionButton from '@/app/components/base/action-button'
import {
  PortalToFollowElem,
  PortalToFollowElemContent,
  PortalToFollowElemTrigger,
} from '@/app/components/base/portal-to-follow-elem'
import ThemeSwitcher from '@/app/components/base/theme-switcher'
import type { SiteInfo } from '@/models/share'
import cn from '@/utils/classnames'
import { AccessMode } from '@/models/access-control'
import { useWebAppStore } from '@/context/web-app-context'

type Props = {
  data?: SiteInfo
  placement?: Placement
  hideLogout?: boolean
}

const MenuDropdown: FC<Props> = ({
  data,
  placement,
  hideLogout,
}) => {
  const webAppAccessMode = useWebAppStore(s => s.webAppAccessMode)
  const router = useRouter()
  const pathname = usePathname()
  const { t } = useTranslation()
  const [open, doSetOpen] = useState(false)
  const openRef = useRef(open)
  const setOpen = useCallback((v: boolean) => {
    doSetOpen(v)
    openRef.current = v
  }, [doSetOpen])

  const handleTrigger = useCallback(() => {
    setOpen(!openRef.current)
  }, [setOpen])

  const handleLogout = useCallback(() => {
    localStorage.removeItem('token')
    localStorage.removeItem('webapp_access_token')
    router.replace(`/webapp-signin?redirect_url=${pathname}`)
  }, [router, pathname])

  const [show, setShow] = useState(false)

  return (
    <>
      <PortalToFollowElem
        open={open}
        onOpenChange={setOpen}
        placement={placement || 'bottom-end'}
        offset={{
          mainAxis: 4,
          crossAxis: -4,
        }}
      >
        <PortalToFollowElemTrigger onClick={handleTrigger}>
          <div>
            <ActionButton size='l' className={cn(open && 'bg-state-base-hover')}>
              <RiEqualizer2Line className='h-[18px] w-[18px]' />
            </ActionButton>
          </div>
        </PortalToFollowElemTrigger>
        <PortalToFollowElemContent className='z-50'>
          <div className='w-[224px] rounded-xl border-[0.5px] border-components-panel-border bg-components-panel-bg-blur shadow-lg backdrop-blur-sm'>
            <div className='p-1'>
              <div className={cn('system-md-regular flex cursor-pointer items-center rounded-lg py-1.5 pl-3 pr-2 text-text-secondary')}>
                <div className='grow'>{t('common.theme.theme')}</div>
                <ThemeSwitcher />
              </div>
            </div>
            <Divider type='horizontal' className='my-0' />
            <div className='p-1'>
              {data?.privacy_policy && (
                <a href={data.privacy_policy} target='_blank' className='system-md-regular flex cursor-pointer items-center rounded-lg px-3 py-1.5 text-text-secondary hover:bg-state-base-hover'>
                  <span className='grow'>{t('share.chat.privacyPolicyMiddle')}</span>
                </a>
              )}
              <div
                onClick={() => {
                  handleTrigger()
                  setShow(true)
                }}
                className='system-md-regular cursor-pointer rounded-lg px-3 py-1.5 text-text-secondary hover:bg-state-base-hover'
              >{t('common.userProfile.about')}</div>
            </div>
            {!(hideLogout || webAppAccessMode === AccessMode.EXTERNAL_MEMBERS || webAppAccessMode === AccessMode.PUBLIC) && (
              <div className='p-1'>
                <div
                  onClick={handleLogout}
                  className='system-md-regular cursor-pointer rounded-lg px-3 py-1.5 text-text-secondary hover:bg-state-base-hover'
                >
                  {t('common.userProfile.logout')}
                </div>
              </div>
            )}
          </div>
        </PortalToFollowElemContent>
      </PortalToFollowElem>
      {show && (
        <InfoModal
          isShow={show}
          onClose={() => {
            setShow(false)
          }}
          data={data}
        />
      )}
    </>
  )
}
export default React.memo(MenuDropdown)
