"use client"

import Link from "next/link"
import { useEnhancedTranslation } from "@/lib/i18n-enhanced"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"

export function EnhancedContactSection() {
  const { t, isRTL } = useEnhancedTranslation()

  return (
    <section className={cn("w-full py-12 md:py-24 lg:py-32", isRTL && "text-right")}>
      <div className="container grid items-center justify-center gap-4 px-4 text-center md:px-6 lg:gap-10">
        <div className="space-y-3">
          <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">{t("contact.title")}</h2>
          <p className="mx-auto max-w-[700px] text-gray-500 md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed dark:text-gray-400">
            {t("contact.subtitle")}
          </p>
        </div>
        <div className="mx-auto w-full max-w-sm space-y-2">
          <form className="flex flex-col space-y-2">
            <Input placeholder={t("contact.name")} type="text" />
            <Input placeholder={t("contact.email")} type="email" />
            <Textarea placeholder={t("contact.message")} />
            <Button type="submit">{t("contact.send")}</Button>
          </form>
          <div className="text-sm text-gray-500 dark:text-gray-400">
            <p>{t("contact.address")}</p>
            <p>{t("contact.phone")}</p>
            <p>
              <Link className="underline" href={`mailto:${t("contact.emailAddress")}`}>
                {t("contact.emailAddress")}
              </Link>
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
